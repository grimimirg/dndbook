import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api.service.js';

export const useUserStore = defineStore('user', () => {
  const isSaving = ref(false);

  async function updateProfile(data) {
    isSaving.value = true;
    try {
      const response = await api.put('/user/profile', data);
      return { success: true, user: response.data.user };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to update profile' 
      };
    } finally {
      isSaving.value = false;
    }
  }

  async function updatePassword(currentPassword, newPassword) {
    try {
      await api.put('/user/password', {
        current_password: currentPassword,
        new_password: newPassword
      });
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to update password' 
      };
    }
  }

  async function uploadAvatar(file) {
    const formData = new FormData();
    formData.append('avatar', file);

    try {
      const response = await api.post('/user/avatar', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      return { 
        success: true, 
        avatar_url: response.data.avatar_url,
        user: response.data.user 
      };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to upload avatar' 
      };
    }
  }

  async function removeAvatar() {
    try {
      const response = await api.put('/user/profile', { avatar_url: null });
      return { success: true, user: response.data.user };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to remove avatar' 
      };
    }
  }

  return {
    isSaving,
    updateProfile,
    updatePassword,
    uploadAvatar,
    removeAvatar
  };
});
