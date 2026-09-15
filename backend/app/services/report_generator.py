from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from sqlalchemy.orm import Session
from app.models import models
import io
from datetime import datetime

def generate_pdf_report(db: Session) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph("NETPULSE - Network Performance Report", styles['Title']))
    story.append(Spacer(1, 12))
    story.append(Paragraph(f"Generated at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC", styles['Normal']))
    story.append(Spacer(1, 12))

    # Overview
    devices = db.query(models.Device).filter(models.Device.is_in_latest_scan == True).all()
    online_count = sum(1 for d in devices if d.status == "ONLINE")
    
    story.append(Paragraph("System Overview", styles['Heading2']))
    story.append(Paragraph(f"Active Discovered Devices (Current Network): {len(devices)}", styles['Normal']))
    story.append(Paragraph(f"Currently Online: {online_count}", styles['Normal']))
    story.append(Spacer(1, 12))

    # Device Table
    story.append(Paragraph("Device Details", styles['Heading2']))
    data = [["IP Address", "Hostname", "Status"]]
    for d in devices:
        data.append([d.ip_address, d.hostname or "Unknown", d.status])
        
    t = Table(data, colWidths=[150, 200, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    story.append(t)
    story.append(Spacer(1, 12))

    # Alerts Summary
    story.append(Paragraph("Recent Unresolved Alerts", styles['Heading2']))
    from sqlalchemy import or_
    device_ids = [d.id for d in devices]
    
    # Filter alerts: Unresolved AND (belongs to current devices OR is a system alert)
    if device_ids:
        alerts_query = db.query(models.Alert).filter(
            models.Alert.resolved == False,
            or_(models.Alert.device_id.in_(device_ids), models.Alert.device_id == None)
        )
    else:
        alerts_query = db.query(models.Alert).filter(
            models.Alert.resolved == False,
            models.Alert.device_id == None
        )
        
    alerts = alerts_query.all()
    
    if alerts:
        alert_data = [["Type", "Severity", "Message"]]
        for a in alerts:
            alert_data.append([a.alert_type, a.severity, a.message])
        at = Table(alert_data, colWidths=[100, 80, 300])
        at.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.indianred),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('GRID', (0,0), (-1,-1), 1, colors.black)
        ]))
        story.append(at)
    else:
        story.append(Paragraph("No active alerts at this time.", styles['Normal']))

    doc.build(story)
    return buffer.getvalue()
