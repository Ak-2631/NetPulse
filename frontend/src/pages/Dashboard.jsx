import { useState, useEffect } from 'react';
import { getSystemInfo, getDevices, getHealthScore, getTraffic, getAlerts } from '../services/api';
import { Activity, Server, ShieldAlert, ArrowUpRight, ArrowDownRight, Wifi, AlertTriangle } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const [sysInfo, setSysInfo] = useState(null);
  const [devices, setDevices] = useState([]);
  const [health, setHealth] = useState(null);
  const [traffic, setTraffic] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [wsStatus, setWsStatus] = useState('DISCONNECTED');
  
  const [trafficHistory, setTrafficHistory] = useState([]);

  const fetchData = async () => {
    try {
      const [sysRes, devRes, healthRes, trafRes, alertRes] = await Promise.all([
        getSystemInfo(),
        getDevices(),
        getHealthScore(),
        getTraffic(),
        getAlerts()
      ]);
      setSysInfo(sysRes.data);
      setDevices(devRes.data);
      setHealth(healthRes.data);
      setTraffic(trafRes.data);
      setAlerts(alertRes.data.filter(a => !a.resolved));

      // Append to traffic history
      setTrafficHistory(prev => {
        const newHist = [...prev, {
          time: new Date().toLocaleTimeString(),
          up: trafRes.data.upload_rate_bps / 1024, // KBps
          down: trafRes.data.download_rate_bps / 1024,
        }];
        if (newHist.length > 20) newHist.shift();
        return newHist;
      });

    } catch (error) {
      console.error("Error fetching dashboard data", error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000);
    
    // WebSocket
    let ws;
    const connectWs = () => {
      setWsStatus('RECONNECTING');
      ws = new WebSocket('ws://localhost:8000/ws');
      ws.onopen = () => setWsStatus('LIVE');
      ws.onclose = () => {
        setWsStatus('DISCONNECTED');
        setTimeout(connectWs, 3000);
      };
      ws.onerror = () => ws.close();
      ws.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'ping') {
            // we could trigger a fast refresh here if needed
        }
      };
    };
    connectWs();

    return () => {
      clearInterval(interval);
      if(ws) ws.close();
    };
  }, []);

  const onlineCount = devices.filter(d => d.status === 'ONLINE').length;
  const offlineCount = devices.length - onlineCount;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-3xl font-bold">Dashboard</h2>
          {sysInfo && (
            <p className="text-slate-400 mt-2">
              Monitoring Host: <span className="text-slate-200">{sysInfo.hostname}</span> ({sysInfo.local_ip})
            </p>
          )}
        </div>
        <div className="flex items-center space-x-2 bg-slate-900 px-4 py-2 rounded-full border border-slate-800">
          <div className={`w-3 h-3 rounded-full ${wsStatus === 'LIVE' ? 'bg-green-500' : wsStatus === 'RECONNECTING' ? 'bg-yellow-500 animate-pulse' : 'bg-red-500'}`}></div>
          <span className="text-sm font-medium">{wsStatus}</span>
        </div>
      </div>

      {/* Demo Mode Notice */}
      <div className="bg-blue-900/30 border border-blue-500/50 p-4 rounded-xl flex items-start space-x-4">
        <Activity className="text-blue-400 shrink-0 mt-1" />
        <div>
          <h4 className="font-semibold text-blue-300">LIVE MODE ACTIVE</h4>
          <p className="text-sm text-blue-200/70 mt-1">
            Displaying real network metrics from the monitoring host's interface. Note that packet capture is limited to traffic visible to this interface on the LAN.
          </p>
        </div>
      </div>

      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Network Health" 
          value={health ? `${health.score}/100` : '-'} 
          icon={<Activity className="text-blue-500" />} 
        />
        <StatCard 
          title="Total Devices" 
          value={devices.length} 
          subValue={`${onlineCount} Online, ${offlineCount} Offline`}
          icon={<Server className="text-indigo-500" />} 
        />
        <StatCard 
          title="Active Alerts" 
          value={alerts.length} 
          icon={<ShieldAlert className={alerts.length > 0 ? "text-red-500" : "text-green-500"} />} 
        />
        <StatCard 
          title="Avg Latency" 
          value={health ? `${health.avg_latency_ms} ms` : '-'} 
          icon={<Wifi className="text-emerald-500" />} 
        />
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Host Interface Traffic</h3>
          <p className="text-xs text-slate-500 mb-6">Traffic measured on {traffic?.interface || 'active interface'}</p>
          <div className="flex space-x-6 mb-6">
            <div className="flex items-center space-x-2">
              <ArrowDownRight className="text-green-400" />
              <div>
                <p className="text-xs text-slate-400">Download</p>
                <p className="font-semibold">{(traffic?.download_rate_bps / 1024).toFixed(1)} KB/s</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <ArrowUpRight className="text-blue-400" />
              <div>
                <p className="text-xs text-slate-400">Upload</p>
                <p className="font-semibold">{(traffic?.upload_rate_bps / 1024).toFixed(1)} KB/s</p>
              </div>
            </div>
          </div>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trafficHistory}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
                <YAxis stroke="#94a3b8" fontSize={12} />
                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                <Line type="monotone" dataKey="down" stroke="#4ade80" name="Download (KB/s)" strokeWidth={2} dot={false} />
                <Line type="monotone" dataKey="up" stroke="#60a5fa" name="Upload (KB/s)" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Recent Alerts</h3>
          <div className="space-y-4">
            {alerts.length === 0 ? (
              <p className="text-slate-400 text-sm">No active alerts.</p>
            ) : (
              alerts.slice(0, 5).map(alert => (
                <div key={alert.id} className="flex items-start space-x-4 p-4 rounded-lg bg-slate-950 border border-slate-800">
                  <AlertTriangle className={`shrink-0 ${alert.severity === 'CRITICAL' ? 'text-red-500' : 'text-yellow-500'}`} />
                  <div>
                    <h4 className="font-medium text-slate-200">{alert.alert_type}</h4>
                    <p className="text-sm text-slate-400 mt-1">{alert.message}</p>
                    <p className="text-xs text-slate-500 mt-2">{new Date(alert.timestamp).toLocaleString()}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ title, value, subValue, icon }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex items-center justify-between">
      <div>
        <p className="text-slate-400 text-sm font-medium">{title}</p>
        <h3 className="text-3xl font-bold text-slate-100 mt-2">{value}</h3>
        {subValue && <p className="text-xs text-slate-500 mt-1">{subValue}</p>}
      </div>
      <div className="p-4 bg-slate-800/50 rounded-full">
        {icon}
      </div>
    </div>
  );
}
