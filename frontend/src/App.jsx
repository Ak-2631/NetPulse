import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Activity, Server, Share2, ShieldAlert, FileText, Wifi, Settings } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Devices from './pages/Devices';
import Topology from './pages/Topology';
import Packets from './pages/Packets';
import Alerts from './pages/Alerts';
import Reports from './pages/Reports';

function Sidebar() {
  const location = useLocation();
  
  const navItems = [
    { path: '/', name: 'Dashboard', icon: <Activity size={20} /> },
    { path: '/devices', name: 'Devices', icon: <Server size={20} /> },
    { path: '/topology', name: 'Network Topology', icon: <Share2 size={20} /> },
    { path: '/packets', name: 'Packet Analyzer', icon: <Wifi size={20} /> },
    { path: '/alerts', name: 'Alerts', icon: <ShieldAlert size={20} /> },
    { path: '/reports', name: 'Reports', icon: <FileText size={20} /> },
  ];

  return (
    <div className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col h-screen sticky top-0">
      <div className="p-6">
        <h1 className="text-2xl font-bold text-blue-500 tracking-wider">NETPULSE</h1>
        <p className="text-xs text-slate-400 mt-1">Smart Network Monitoring</p>
      </div>
      <nav className="flex-1 px-4 py-4 space-y-2">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors ${
                isActive 
                  ? 'bg-blue-600 text-white' 
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              {item.icon}
              <span className="font-medium">{item.name}</span>
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-slate-800">
        <div className="flex items-center space-x-3 px-4 py-3 rounded-lg text-slate-400 hover:bg-slate-800 hover:text-white cursor-pointer transition-colors">
          <Settings size={20} />
          <span className="font-medium">Settings</span>
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <Router>
      <div className="flex min-h-screen bg-slate-950 text-slate-50">
        <Sidebar />
        <main className="flex-1 p-8 overflow-y-auto h-screen">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/devices" element={<Devices />} />
            <Route path="/topology" element={<Topology />} />
            <Route path="/packets" element={<Packets />} />
            <Route path="/alerts" element={<Alerts />} />
            <Route path="/reports" element={<Reports />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
