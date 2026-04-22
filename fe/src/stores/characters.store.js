import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api.service.js';

export const useCharactersStore = defineStore('characters', () => {
  const characters = ref([]);
  const loading = ref(false);

  async function fetchCharacters(campaignId) {
    if (!campaignId) {
      characters.value = [];
      return;
    }

    loading.value = true;
    try {
      const response = await api.get(`/campaigns/${campaignId}/characters`);
      characters.value = response.data || [];
    } catch (error) {
      console.error('Failed to fetch characters:', error);
      characters.value = [];
    } finally {
      loading.value = false;
    }
  }

  async function createCharacter(campaignId, formData) {
    try {
      const response = await api.post(`/campaigns/${campaignId}/characters`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      characters.value.unshift(response.data);
      return { success: true, character: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to create character'
      };
    }
  }

  async function updateCharacter(campaignId, characterId, formData) {
    try {
      const response = await api.put(`/campaigns/${campaignId}/characters/${characterId}`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      const index = characters.value.findIndex(c => c.id === characterId);
      if (index !== -1) {
        characters.value[index] = response.data;
      }
      return { success: true, character: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to update character'
      };
    }
  }

  async function deleteCharacter(campaignId, characterId) {
    try {
      await api.delete(`/campaigns/${campaignId}/characters/${characterId}`);
      characters.value = characters.value.filter(c => c.id !== characterId);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to delete character'
      };
    }
  }

  function $reset() {
    characters.value = [];
    loading.value = false;
  }

  return {
    characters,
    loading,
    fetchCharacters,
    createCharacter,
    updateCharacter,
    deleteCharacter,
    $reset
  };
});
