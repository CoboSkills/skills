import axios from 'axios';

// Detect base path: if running under /node, use /node/api; otherwise /api
const basePath = window.location.pathname.startsWith('/node') ? '/node/api' : '/api';
const API = axios.create({ baseURL: basePath, timeout: 10000 });

export const client = {
  // Status
  getStatus: () => API.get('/status'),
  getMonitor: () => API.get('/monitor'),
  
  // Tasks (synced from hub, actions report to hub)
  getTasks: () => API.get('/tasks'),
  startTask: (id: string) => API.post(`/tasks/${id}/start`),
  completeTask: (id: string, result?: any) => API.post(`/tasks/${id}/complete`, { result }),
  failTask: (id: string, error?: string) => API.post(`/tasks/${id}/fail`, { error }),
  
  // Skills (local scan, read-only)
  getSkills: () => API.get('/skills'),
  refreshSkills: () => API.post('/skills/refresh'),
  
  // Memory (local CRUD)
  getMemory: (params?: any) => API.get('/memory', { params }),
  createMemory: (data: any) => API.post('/memory', data),
  updateMemory: (id: string, data: any) => API.put(`/memory/${id}`, data),
  deleteMemory: (id: string) => API.delete(`/memory/${id}`),
  
  // Connection
  getConnection: () => API.get('/connection'),
  reconnect: () => API.post('/connection/reconnect'),
};

export default client;
