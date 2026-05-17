import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api.service.js';
import socketService from '../services/socket.service.js';
import { SocketEvents } from '../constants/socketConstants.js';

export const useInvitesStore = defineStore('invites', () => {
  const invites = ref([]);
  const loading = ref(false);
  const toastQueue = ref([]);

  async function fetchInvites() {
    loading.value = true;
    try {
      const response = await api.get('/invites');
      invites.value = response.data;
    } catch (error) {
      console.error('Failed to fetch invites:', error);
    } finally {
      loading.value = false;
    }
  }

  async function acceptInvite(inviteId) {
    try {
      const response = await api.post(`/invites/${inviteId}/accept`);
      
      invites.value = invites.value.filter(inv => inv.id !== inviteId);
      
      return { success: true, campaign: response.data.campaign };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to accept invite' 
      };
    }
  }

  async function rejectInvite(inviteId) {
    try {
      await api.post(`/invites/${inviteId}/reject`);
      
      invites.value = invites.value.filter(inv => inv.id !== inviteId);
      
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to reject invite' 
      };
    }
  }

  async function inviteUsers(campaignId, userIds) {
    try {
      const response = await api.post(`/invites/campaign/${campaignId}`, {
        user_ids: userIds
      });
      return { success: true, data: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to send invites' 
      };
    }
  }

  async function getAvailableUsers(campaignId) {
    try {
      const response = await api.get(`/invites/available-users/${campaignId}`);
      return { success: true, users: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to fetch available users' 
      };
    }
  }

  function addInvite(invite) {
    const exists = invites.value.find(inv => inv.id === invite.id);
    if (!exists) {
      invites.value.push(invite);
    }
  }

  function showToast(toast) {
    toastQueue.value.push({
      id: Date.now(),
      ...toast
    });
    
    setTimeout(() => {
      toastQueue.value.shift();
    }, 5000);
  }

  function removeToast(toastId) {
    toastQueue.value = toastQueue.value.filter(t => t.id !== toastId);
  }

  function setupSocketListener() {
    socketService.on(SocketEvents.NEW_INVITE, (data) => {
      addInvite({
        id: data.id,
        campaign_id: data.campaign_id,
        campaign_name: data.campaign_name,
        inviter_id: data.inviter_id,
        inviter_username: data.inviter_username,
        status: 'pending'
      });
      
      showToast({
        inviter: data.inviter_username,
        campaign: data.campaign_name
      });
    });
  }

  function $reset() {
    invites.value = [];
    loading.value = false;
    toastQueue.value = [];
  }

  return {
    invites,
    loading,
    toastQueue,
    fetchInvites,
    acceptInvite,
    rejectInvite,
    inviteUsers,
    getAvailableUsers,
    addInvite,
    showToast,
    removeToast,
    setupSocketListener,
    $reset
  };
});
