import axios from 'axios';

const API_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_URL,
});

export const getSystemInfo = () => api.get('/system');
export const getHealthCheck = () => api.get('/health');

export const getDevices = () => api.get('/devices');
export const startScan = () => api.post('/devices/scan');

export const getHealthScore = () => api.get('/metrics/health-score');
export const getDeviceMetrics = (id) => api.get(`/metrics/${id}`);

export const getTraffic = () => api.get('/traffic');

export const getAlerts = () => api.get('/alerts');
export const acknowledgeAlert = (id) => api.patch(`/alerts/${id}/acknowledge`);

export const startCapture = () => api.post('/packets/start');
export const stopCapture = () => api.post('/packets/stop');
export const getPacketStatus = () => api.get('/packets/status');
export const getRecentPackets = () => api.get('/packets/recent');
export const getPacketStats = () => api.get('/packets/stats');

export const getTopology = () => api.get('/topology');

export const generateReport = async () => {
  try {
    const response = await api.get('/reports/generate', { responseType: 'blob' });
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', 'netpulse_report.pdf');
    document.body.appendChild(link);
    link.click();
    link.parentNode.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Failed to generate report', error);
  }
};

export default api;
