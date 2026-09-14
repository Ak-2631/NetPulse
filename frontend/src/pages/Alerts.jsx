import { useState, useEffect } from 'react';
import { getAlerts, acknowledgeAlert } from '../services/api';
import { ShieldAlert, CheckCircle, Clock, Server } from 'lucide-react';

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [filter, setFilter] = useState('all');

  const fetchAlerts = async () => {
    try {
      const res = await getAlerts();
      setAlerts(res.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(fetchAlerts, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleAcknowledge = async (id) => {
    try {
      await acknowledgeAlert(id);
      fetchAlerts();
    } catch (error) {
      console.error(error);
    }
  };

  const filteredAlerts = alerts.filter(a => {
    if (filter === 'unacknowledged') return !a.acknowledged;
    if (filter === 'active') return !a.resolved;
    return true;
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Alerts</h2>
        <div className="flex space-x-2 bg-slate-900 p-1 rounded-lg border border-slate-800">
          {['all', 'active', 'unacknowledged'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-colors ${
                filter === f ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="text-center py-12 bg-slate-900 border border-slate-800 rounded-xl">
            <CheckCircle className="mx-auto text-green-500 mb-3" size={48} />
            <h3 className="text-lg font-medium text-slate-200">All clear</h3>
            <p className="text-slate-400">No alerts matching this filter.</p>
          </div>
        ) : (
          filteredAlerts.map(alert => (
            <div key={alert.id} className={`p-5 rounded-xl border flex justify-between items-start ${
              alert.severity === 'CRITICAL' 
                ? 'bg-red-500/10 border-red-500/20' 
                : 'bg-yellow-500/10 border-yellow-500/20'
            }`}>
              <div className="flex space-x-4">
                <ShieldAlert className={`shrink-0 mt-1 ${alert.severity === 'CRITICAL' ? 'text-red-400' : 'text-yellow-400'}`} size={24} />
                <div>
                  <div className="flex items-center space-x-3">
                    <h4 className="text-lg font-bold text-slate-100">{alert.alert_type}</h4>
                    {alert.resolved && (
                      <span className="bg-green-500/20 text-green-400 px-2 py-0.5 rounded text-xs font-semibold">
                        RESOLVED
                      </span>
                    )}
                  </div>
                  <p className="text-slate-300 mt-1">{alert.message}</p>
                  <div className="flex flex-wrap items-center space-x-4 mt-3 text-xs text-slate-500">
                    <span className="flex items-center space-x-1"><Server size={12}/> <span>{alert.device}</span></span>
                    <span className="flex items-center space-x-1"><Clock size={12}/> <span>{new Date(alert.timestamp).toLocaleString()}</span></span>
                  </div>
                </div>
              </div>
              
              {!alert.acknowledged && (
                <button 
                  onClick={() => handleAcknowledge(alert.id)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded-lg text-sm font-medium transition-colors"
                >
                  Acknowledge
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
