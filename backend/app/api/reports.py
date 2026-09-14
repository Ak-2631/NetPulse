from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.report_generator import generate_pdf_report

router = APIRouter()

@router.get("/generate")
def get_report(db: Session = Depends(get_db)):
    pdf_bytes = generate_pdf_report(db)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=netpulse_report.pdf"}
    )
