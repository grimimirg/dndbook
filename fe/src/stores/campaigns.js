import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const useCampaignsStore = defineStore('campaigns', () => {
  const campaigns = ref([])
  const currentCampaign = ref(null)
  const loading = ref(false)

  async function fetchCampaigns() {
    loading.value = true
    try {
      const response = await api.get('/api/campaigns')
      campaigns.value = response.data
    } catch (error) {
      console.error('Failed to fetch campaigns:', error)
    } finally {
      loading.value = false
    }
  }

  async function createCampaign(name, description) {
    try {
      const response = await api.post('/api/campaigns', { name, description })
      campaigns.value.push(response.data)
      return { success: true, campaign: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to create campaign' 
      }
    }
  }

  async function updateCampaign(id, data) {
    try {
      const response = await api.put(`/api/campaigns/${id}`, data)
      const index = campaigns.value.findIndex(c => c.id === id)
      if (index !== -1) {
        campaigns.value[index] = response.data
      }
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to update campaign' 
      }
    }
  }

  async function deleteCampaign(id) {
    try {
      await api.delete(`/api/campaigns/${id}`)
      campaigns.value = campaigns.value.filter(c => c.id !== id)
      if (currentCampaign.value?.id === id) {
        currentCampaign.value = null
      }
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to delete campaign' 
      }
    }
  }

  function setCurrentCampaign(campaign) {
    currentCampaign.value = campaign
  }

  return {
    campaigns,
    currentCampaign,
    loading,
    fetchCampaigns,
    createCampaign,
    updateCampaign,
    deleteCampaign,
    setCurrentCampaign
  }
})
