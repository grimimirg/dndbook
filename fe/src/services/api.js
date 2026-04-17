import axios from 'axios'
import { mockApi } from './mockData'

const isMockMode = import.meta.env.VITE_MOCK_DATA === 'true'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json'
  }
})

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

const apiWrapper = {
  get(url, config) {
    if (isMockMode) {
      if (url === '/api/campaigns') {
        return mockApi.getCampaigns()
      }
      if (url.match(/\/api\/campaigns\/\d+\/posts/)) {
        const campaignId = parseInt(url.match(/\/api\/campaigns\/(\d+)\/posts/)[1])
        return mockApi.getCampaignPosts(campaignId, config?.params || {})
      }
    }
    return api.get(url, config)
  },
  
  post(url, data, config) {
    if (isMockMode) {
      if (url === '/api/auth/login') {
        return mockApi.login(data.username, data.password)
      }
      if (url === '/api/auth/register') {
        return mockApi.register(data.username, data.email, data.password)
      }
      if (url === '/api/campaigns') {
        return mockApi.createCampaign(data)
      }
      if (url === '/api/posts') {
        return mockApi.createPost(data)
      }
    }
    return api.post(url, data, config)
  },
  
  put(url, data, config) {
    return api.put(url, data, config)
  },
  
  delete(url, config) {
    return api.delete(url, config)
  }
}

export default apiWrapper
