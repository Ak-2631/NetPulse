import { useState, useEffect } from 'react';
import { getDevices, startScan } from '../services/api';
import { Search, RefreshCw, Server, Clock } from 'lucide-react';

export default function Devices() {
  const [devices, setDevices] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [message, setMessage] = useState('');

  const fetchDevices = async () => {
    try {
      const res = await getDevices();
      setDevices(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleScan = async () => {
    setScanning(true);
    setMessage('');
    try {
      const res = await startScan();
      setMessage(res.data.message);
    } catch (error) {
      setMessage('Scan failed to start.');
    }
    setTimeout(() => {
      setScanning(false);
      setMessage('');
    }, 5000);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Discovered Devices</h2>
        <button 
          onClick={handleScan}
          disabled={scanning}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-colors ${
            scanning ? 'bg-blue-600/50 text-blue-200 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700 text-white'
          }`}
        >
          <Search size={18} className={scanning ? "animate-pulse" : ""} />
          <span>{scanning ? 'Scanning Network...' : 'Scan Subnet'}</span>
        </button>
      </div>
      
      {message && (
        <div className="p-4 bg-blue-900/40 border border-blue-500/50 rounded-lg text-blue-200">
          {message}
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left">
            <thead className="bg-slate-950 border-b border-slate-800">
              <tr>
                <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Device</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">IP / MAC</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Status</th>
                <th className="px-6 py-4 text-xs font-semibold text-slate-400 uppercase tracking-wider">Last Seen</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {devices.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-8 text-center text-slate-500">
                    No devices discovered yet. Click Scan Subnet.
                  </td>
                </tr>
              ) : (
                devices.map(device => (
                  <tr key={device.id} className="hover:bg-slate-800/50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-3">
                        <div className="p-2 bg-slate-800 rounded-lg">
                          <Server size={18} className="text-blue-400" />
                        </div>
                        <span className="font-medium text-slate-200">{device.hostname || 'Unknown Device'}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-slate-200">{device.ip_address}</div>
                      <div className="text-xs text-slate-500">{device.mac_address || 'Unknown MAC'}</div>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${
                        device.status === 'ONLINE' 
                          ? 'bg-green-500/10 text-green-400 border-green-500/20' 
                          : 'bg-red-500/10 text-red-400 border-red-500/20'
                      }`}>
                        {device.status}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex items-center space-x-2 text-sm text-slate-400">
                        <Clock size={14} />
                        <span>{new Date(device.last_seen).toLocaleTimeString()}</span>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
