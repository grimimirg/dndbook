import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api.service.js';

export const useCampaignsStore = defineStore('campaigns', () => {
  const ownedCampaigns = ref([]);
  const sharedCampaigns = ref([]);
  const currentCampaign = ref(null);
  const loading = ref(false);

  async function fetchCampaigns() {
    loading.value = true;
    try {
      const response = await api.get('/api/campaigns');
      ownedCampaigns.value = response.data.owned || [];
      sharedCampaigns.value = response.data.shared || [];
    } catch (error) {
      console.error('Failed to fetch campaigns:', error);
    } finally {
      loading.value = false;
    }
  }

  async function createCampaign(name, description) {
    try {
      const response = await api.post('/api/campaigns', { name, description });
      ownedCampaigns.value.push(response.data);
      return { success: true, campaign: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to create campaign' 
      };
    }
  }

  async function updateCampaign(id, data) {
    try {
      const response = await api.put(`/api/campaigns/${id}`, data);
      const ownedIndex = ownedCampaigns.value.findIndex(c => c.id === id);
      const sharedIndex = sharedCampaigns.value.findIndex(c => c.id === id);
      
      if (ownedIndex !== -1) {
        ownedCampaigns.value[ownedIndex] = response.data;
      } else if (sharedIndex !== -1) {
        sharedCampaigns.value[sharedIndex] = response.data;
      }
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to update campaign' 
      };
    }
  }

  async function deleteCampaign(id) {
    try {
      await api.delete(`/api/campaigns/${id}`);
      ownedCampaigns.value = ownedCampaigns.value.filter(c => c.id !== id);
      sharedCampaigns.value = sharedCampaigns.value.filter(c => c.id !== id);
      if (currentCampaign.value?.id === id) {
        currentCampaign.value = null;
      }
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to delete campaign' 
      };
    }
  }

  function setCurrentCampaign(campaign) {
    currentCampaign.value = campaign;
  }

  function addSharedCampaign(campaign) {
    const exists = sharedCampaigns.value.find(c => c.id === campaign.id);
    if (!exists) {
      sharedCampaigns.value.push(campaign);
    }
  }

  return {
    ownedCampaigns,
    sharedCampaigns,
    currentCampaign,
    loading,
    fetchCampaigns,
    createCampaign,
    updateCampaign,
    deleteCampaign,
    setCurrentCampaign,
    addSharedCampaign
  };
});
