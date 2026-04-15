import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

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
  register: (data) => api.post('/api/auth/register', data),
  login: (data) => api.post('/api/auth/login', data),
  getCurrentUser: () => api.get('/api/auth/me'),
};

export const membersAPI = {
  create: (data) => api.post('/api/members', data),
  getAll: (params) => api.get('/api/members', { params }),
  getById: (id) => api.get(`/api/members/${id}`),
  update: (id, data) => api.put(`/api/members/${id}`, data),
  delete: (id) => api.delete(`/api/members/${id}`),
};

export const teamsAPI = {
  create: (data) => api.post('/api/teams', data),
  getAll: (params) => api.get('/api/teams', { params }),
  getById: (id) => api.get(`/api/teams/${id}`),
  update: (id, data) => api.put(`/api/teams/${id}`, data),
  delete: (id) => api.delete(`/api/teams/${id}`),
};

export const achievementsAPI = {
  create: (data) => api.post('/api/achievements', data),
  getAll: (params) => api.get('/api/achievements', { params }),
  getById: (id) => api.get(`/api/achievements/${id}`),
  update: (id, data) => api.put(`/api/achievements/${id}`, data),
  delete: (id) => api.delete(`/api/achievements/${id}`),
};

export const insightsAPI = {
  get: () => api.get('/api/insights'),
};

export default api;
