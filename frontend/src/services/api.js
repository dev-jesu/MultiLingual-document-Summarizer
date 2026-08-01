import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 180000,
});

export const uploadDocument = (formData) => api.post('/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});

export const summarizeDocument = (formData) => api.post('/summarize', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});

export default api;
