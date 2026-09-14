import { useState, useEffect } from 'react';
import { getPacketStatus, startCapture, stopCapture, getRecentPackets, getPacketStats } from '../services/api';
import { Play, Square, Trash2, Activity } from 'lucide-react';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip, Legend } from 'recharts';

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#64748b'];

export default function Packets() {
  const [isRunning, setIsRunning] = useState(false);
  const [packets, setPackets] = useState([]);
  const [stats, setStats] = useState({ total: 0, distribution: [] });

  const fetchData = async () => {
    try {
      const [statusRes, pktsRes, statsRes] = await Promise.all([
        getPacketStatus(),
        getRecentPackets(),
        getPacketStats()
      ]);
      setIsRunning(statusRes.data.is_running);
      setPackets(pktsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000); // Polling for packets
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    await startCapture();
    fetchData();
  };

  const handleStop = async () => {
    await stopCapture();
    fetchData();
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-3xl font-bold">Packet Analyzer</h2>
        <div className="flex space-x-3">
          {!isRunning ? (
            <button onClick={handleStart} className="flex items-center space-x-2 bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
              <Play size={18} />
              <span>Start Capture</span>
            </button>
          ) : (
            <button onClick={handleStop} className="flex items-center space-x-2 bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium transition-colors">
              <Square size={18} />
              <span>Stop Capture</span>
            </button>
          )}
        </div>
      </div>

      <div className="bg-slate-900/50 border border-slate-800 p-4 rounded-xl flex items-start space-x-4">
        <Activity className="text-slate-400 shrink-0 mt-1" />
        <div>
          <p className="text-sm text-slate-300">
            <strong>Capture Limitation:</strong> This tool captures traffic using the monitoring host's network interface. On a switched network (like most modern LANs), you will generally only see traffic destined for this host, broadcast traffic (like ARP), and multicast traffic. It cannot magically intercept unicast traffic between other PCs without port mirroring configured on the physical switch.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1 bg-slate-900 border border-slate-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4">Protocol Distribution</h3>
          {stats.total > 0 ? (
            <div className="h-64">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats.distribution}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={80}
                    paddingAngle={5}
                    dataKey="count"
                    nameKey="protocol"
                  >
                    {stats.distribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <RechartsTooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
              <div className="text-center mt-4 text-slate-400 text-sm">
                Total Packets: <span className="font-bold text-white">{stats.total}</span>
              </div>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-500">
              No packets captured yet.
            </div>
          )}
        </div>

        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl overflow-hidden flex flex-col h-[400px]">
          <div className="p-4 border-b border-slate-800 bg-slate-950 flex justify-between items-center">
            <h3 className="font-semibold">Recent Packets</h3>
            <span className="text-xs text-slate-500">Showing last 100 packets</span>
          </div>
          <div className="overflow-auto flex-1">
            <table className="w-full text-left text-sm">
              <thead className="bg-slate-900 sticky top-0">
                <tr>
                  <th className="px-4 py-3 font-semibold text-slate-400">Time</th>
                  <th className="px-4 py-3 font-semibold text-slate-400">Source</th>
                  <th className="px-4 py-3 font-semibold text-slate-400">Destination</th>
                  <th className="px-4 py-3 font-semibold text-slate-400">Protocol</th>
                  <th className="px-4 py-3 font-semibold text-slate-400">Length</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {packets.length === 0 ? (
                  <tr>
                    <td colSpan="5" className="px-4 py-8 text-center text-slate-500">
                      Waiting for packets...
                    </td>
                  </tr>
                ) : (
                  packets.map(pkt => (
                    <tr key={pkt.id} className="hover:bg-slate-800/50">
                      <td className="px-4 py-2 text-slate-400">{new Date(pkt.timestamp).toLocaleTimeString()}</td>
                      <td className="px-4 py-2 text-slate-200">{pkt.source_ip}{pkt.source_port ? `:${pkt.source_port}` : ''}</td>
                      <td className="px-4 py-2 text-slate-200">{pkt.destination_ip}{pkt.destination_port ? `:${pkt.destination_port}` : ''}</td>
                      <td className="px-4 py-2 font-medium">
                        <span className={`px-2 py-0.5 rounded text-xs ${
                          pkt.protocol === 'TCP' ? 'bg-blue-500/20 text-blue-400' :
                          pkt.protocol === 'UDP' ? 'bg-green-500/20 text-green-400' :
                          pkt.protocol === 'ICMP' ? 'bg-red-500/20 text-red-400' :
                          'bg-slate-500/20 text-slate-400'
                        }`}>
                          {pkt.protocol}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-slate-400">{pkt.length}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
