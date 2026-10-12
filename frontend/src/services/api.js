import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 180000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const uploadDocument = (formData) => api.post('/upload', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});

export const summarizeDocument = (formData) => api.post('/summarize', formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});

export const exportSummary = async (format, payload) => {
  const response = await api.post(`/export/${format}`, payload, {
    responseType: 'blob',
    headers: { 'Content-Type': 'application/json' },
  });

  // Extract filename from Content-Disposition header if available
  let filename = `${payload.filename?.replace(/\.[^/.]+$/, '') || 'document'}_summary.${format}`;
  const disposition = response.headers['content-disposition'];
  if (disposition && disposition.includes('filename=')) {
    const match = disposition.match(/filename="?([^";]+)"?/);
    if (match && match[1]) {
      filename = match[1];
    }
  }

  // Create blob download link
  const blob = new Blob([response.data], { type: response.headers['content-type'] });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.setAttribute('download', filename);
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
  return filename;
};

// ── Admin API ────────────────────────────────────────────────

export const adminApi = {
  getStats: () => api.get('/admin/stats'),
  
  // Cases
  listCases: () => api.get('/admin/cases'),
  getCase: (caseId) => api.get(`/admin/cases/${caseId}`),
  createCase: (data) => api.post('/admin/cases', data),
  
  // Advocates
  listAdvocates: () => api.get('/admin/advocates'),
  getAdvocateCases: (advocateId) => api.get(`/admin/advocates/${advocateId}/cases`),
  
  // Enrollment
  enrollAdvocate: (caseId, advocateId, role = 'advocate') =>
    api.post(`/admin/cases/${caseId}/enroll`, { advocate_id: advocateId, role }),
  removeMember: (caseId, memberId) =>
    api.delete(`/admin/cases/${caseId}/members/${memberId}`),
  
  // Document Allocation
  allocateDocument: (caseId, formData) =>
    api.post(`/admin/cases/${caseId}/allocate-document`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  removeDocument: (caseId, documentId) =>
    api.delete(`/admin/cases/${caseId}/documents/${documentId}`),
  
  // All users
  listUsers: () => api.get('/admin/users'),
};

export default api;
