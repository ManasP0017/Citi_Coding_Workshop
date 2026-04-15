import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:3001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const authAPI = {
  register: (data) => api.post('/api/auth-service/register', data),
  login: (data) => api.post('/api/auth-service/login', data),
  getCurrentUser: () => api.get('/api/auth-service/me'),
};

export const membersAPI = {
  create: (data) => api.post('/api/members-service', data),
  getAll: (params) => api.get('/api/members-service', { params }),
  getById: (id) => api.get(`/api/members-service/${id}`),
  update: (id, data) => api.put(`/api/members-service/${id}`, data),
  delete: (id) => api.delete(`/api/members-service/${id}`),
};

export const teamsAPI = {
  create: (data) => api.post('/api/teams-service', data),
  getAll: (params) => api.get('/api/teams-service', { params }),
  getById: (id) => api.get(`/api/teams-service/${id}`),
  update: (id, data) => api.put(`/api/teams-service/${id}`, data),
  delete: (id) => api.delete(`/api/teams-service/${id}`),
};

export const achievementsAPI = {
  create: (data) => api.post('/api/achievements-service', data),
  getAll: (params) => api.get('/api/achievements-service', { params }),
  getById: (id) => api.get(`/api/achievements-service/${id}`),
  update: (id, data) => api.put(`/api/achievements-service/${id}`, data),
  delete: (id) => api.delete(`/api/achievements-service/${id}`),
};

export const insightsAPI = {
  get: () => api.get('/api/insights-service'),
};

export default api;
