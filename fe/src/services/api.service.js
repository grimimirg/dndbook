import axios from 'axios';
import { mockApi } from './mockData.service.js';

const isMockMode = import.meta.env.VITE_MOCK_DATA === 'true';

const apiService = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
});

apiService.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiService.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

const apiWrapper = {
  get(url, config) {
    if (isMockMode) {
      if (url === '/apiService/campaigns') {
        return mockApi.getCampaigns();
      }
      if (url.match(/\/apiService\/campaigns\/\d+\/posts/)) {
        const campaignId = parseInt(url.match(/\/apiService\/campaigns\/(\d+)\/posts/)[1]);
        return mockApi.getCampaignPosts(campaignId, config?.params || {});
      }
    }
    return apiService.get(url, config);
  },
  
  post(url, data, config) {
    if (isMockMode) {
      if (url === '/apiService/auth/login') {
        return mockApi.login(data.username, data.password);
      }
      if (url === '/apiService/auth/register') {
        return mockApi.register(data.username, data.email, data.password);
      }
      if (url === '/apiService/campaigns') {
        return mockApi.createCampaign(data);
      }
      if (url === '/apiService/posts') {
        return mockApi.createPost(data);
      }
      if (url.match(/\/apiService\/posts\/\d+\/images/)) {
        const postId = parseInt(url.match(/\/apiService\/posts\/(\d+)\/images/)[1]);
        return mockApi.uploadImage(postId, data);
      }
    }
    return apiService.post(url, data, config);
  },
  
  put(url, data, config) {
    return apiService.put(url, data, config);
  },
  
  delete(url, config) {
    return apiService.delete(url, config);
  }
};

export default apiWrapper;
