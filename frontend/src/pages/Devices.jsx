import { useState, useEffect } from 'react';
import { getDevices, startScan, getSystemInfo } from '../services/api';
import { Search, RefreshCw, Server, Clock } from 'lucide-react';

export default function Devices() {
  const [devices, setDevices] = useState([]);
  const [scanning, setScanning] = useState(false);
  const [message, setMessage] = useState('');

  const [sysInfo, setSysInfo] = useState(null);

  const fetchData = async () => {
    try {
      const [devRes, sysRes] = await Promise.all([
        getDevices(),
        getSystemInfo()
      ]);
      setDevices(devRes.data);
      setSysInfo(sysRes.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleScan = async () => {
    setScanning(true);
    setMessage('');
    try {
      const res = await startScan();
      setMessage(res.data.message);
    } catch (error) {
      setMessage(error.response?.data?.detail || 'Scan failed to start.');
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
      
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex justify-between items-center text-sm mb-4">
        <div className="flex space-x-6">
          <div>
            <span className="text-slate-500">Active Interface:</span>
            <span className="ml-2 font-medium text-slate-200">{sysInfo?.active_interface || 'Detecting...'}</span>
          </div>
          <div>
            <span className="text-slate-500">Local IP:</span>
            <span className="ml-2 font-medium text-slate-200">{sysInfo?.local_ip || '...'}</span>
          </div>
          <div>
            <span className="text-slate-500">Target Subnet:</span>
            <span className="ml-2 font-medium text-blue-400">{sysInfo?.subnet || '...'}</span>
          </div>
        </div>
      </div>

      {sysInfo && sysInfo.pcap_available === false && (
        <div className="p-4 bg-yellow-900/30 border border-yellow-500/50 rounded-lg text-yellow-200 mb-4 text-sm">
          <strong>Discovery Mode: ICMP Fallback.</strong> Npcap is not installed on this system. Devices are being discovered via Ping instead of ARP. 
          Layer-2 MAC addresses cannot be retrieved through ICMP scanning.
        </div>
      )}
      
      {sysInfo && sysInfo.pcap_available === true && (
        <div className="p-4 bg-green-900/30 border border-green-500/50 rounded-lg text-green-200 mb-4 text-sm">
          <strong>Discovery Mode: ARP (Scapy).</strong> Npcap is detected. Full Layer-2 discovery and MAC address resolution is active.
        </div>
      )}

      {message && (
        <div className={`p-4 border rounded-lg mb-4 ${
          message.includes('failed') ? 'bg-red-900/40 border-red-500/50 text-red-200' : 'bg-blue-900/40 border-blue-500/50 text-blue-200'
        }`}>
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
                      <div className="text-xs text-slate-500">
                        {device.mac_address ? device.mac_address : (sysInfo?.pcap_available ? 'Unknown MAC' : 'MAC Unavailable (ICMP Mode)')}
                      </div>
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
