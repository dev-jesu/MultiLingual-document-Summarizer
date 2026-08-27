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

export default api;
