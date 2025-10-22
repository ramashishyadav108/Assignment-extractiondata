import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const uploadFiles = async (files, templateId) => {
  const formData = new FormData();
  
  // The new backend only supports single file upload
  const file = files[0];
  formData.append('file', file);
  formData.append('template_id', templateId || 'fund_report_v1');
  
  const response = await api.post('/extract', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getJobStatus = async (jobId) => {
  // For the new backend, this is not needed as extraction is synchronous
  // Return completed status
  return { status: 'completed', job_id: jobId };
};

export const getExtractionResults = async (jobId) => {
  // For the new backend, results are returned immediately from upload
  // This is just a placeholder
  return { success: true, output_file: jobId };
};

export const downloadResult = (filename) => {
  return `${API_BASE_URL}/download/${filename}`;
};

export const getExtractionHistory = async () => {
  const response = await api.get('/results');
  return response.data;
};

export const downloadFile = async (filename) => {
  const url = `${API_BASE_URL}/download/${filename}`;
  window.open(url, '_blank');
};

export default api;

