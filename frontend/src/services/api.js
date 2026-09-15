import axios from 'axios';

export const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
});

export const getSystemInfo = () => api.get('/system');
export const getHealthCheck = () => api.get('/health');

export const getDevices = (view = 'current') => api.get(`/devices?view=${view}`);
export const startScan = () => api.post('/devices/scan');

export const getHealthScore = () => api.get('/metrics/health-score');
export const getDeviceMetrics = (id) => api.get(`/metrics/${id}`);

export const getTraffic = () => api.get('/traffic');

export const getAlerts = () => api.get('/alerts');
export const acknowledgeAlert = (id) => api.patch(`/alerts/${id}/acknowledge`);

export const startCapture = () => api.post('/packets/start');
export const stopCapture = () => api.post('/packets/stop');
export const getPacketStatus = () => api.get('/packets/status');
export const getRecentPackets = (view = 'current') => api.get(`/packets/recent?view=${view}`);
export const getPacketStats = (view = 'current') => api.get(`/packets/stats?view=${view}`);

export const getTopology = (view = 'current') => api.get(`/topology?view=${view}`);


export default api;
