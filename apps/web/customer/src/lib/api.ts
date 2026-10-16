import axios from 'axios';

const baseURL = import.meta.env.VITE_API_URL || 'https://smartresort-backend-8rac.onrender.com/api/v1';

export const api = axios.create({
  baseURL,
  timeout: 10_000,
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
