import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
});

export const uploadFiles = async (files, templateId) => {
  const formData = new FormData();
  
  files.forEach((file) => {
    formData.append('files', file);
  });
  
  formData.append('template_id', templateId);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  
  return response.data;
};

export const getJobStatus = async (jobId) => {
  const response = await api.get(`/status/${jobId}`);
  return response.data;
};

export const getExtractionResults = async (jobId) => {
  const response = await api.get(`/results/${jobId}`);
  return response.data;
};

export const downloadResult = (jobId) => {
  return `${API_BASE_URL}/download/${jobId}`;
};

export default api;
