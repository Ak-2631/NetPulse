import { API_URL } from '../services/api';
import { FileText, Download } from 'lucide-react';

export default function Reports() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold">Reports</h2>

      <div className="bg-slate-900 border border-slate-800 rounded-xl p-8 text-center max-w-2xl mx-auto mt-12">
        <FileText size={64} className="mx-auto text-blue-500 mb-6" />
        <h3 className="text-2xl font-semibold mb-3">Network Performance Report</h3>
        <p className="text-slate-400 mb-8 max-w-md mx-auto">
          Generate a comprehensive PDF report containing device status, health scores, alert history, and protocol analytics.
        </p>
        
        <a 
          href={`${API_URL}/reports/generate`}
          download="netpulse_report.pdf"
          className="inline-flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold mx-auto transition-colors"
        >
          <Download size={20} />
          <span>Download PDF Report</span>
        </a>
      </div>
    </div>
  );
}
