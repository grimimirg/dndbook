<template>
  <div class="notification-bell">
    <button @click="toggleDropdown" class="bell-button" :class="{ 'has-notifications': invitesStore.invites.length > 0 }">
      <span class="bell-icon">🔔</span>
      <span v-if="invitesStore.invites.length > 0" class="badge">{{ invitesStore.invites.length }}</span>
    </button>
    
    <div v-if="showDropdown" class="dropdown" @click.stop>
      <div class="dropdown-header">
        <h3>{{ t('invite.notifications') }}</h3>
        <button @click="showDropdown = false" class="close-btn">×</button>
      </div>
      
      <div v-if="invitesStore.loading" class="loading">
        {{ t('common.loading') }}
      </div>
      
      <div v-else-if="invitesStore.invites.length === 0" class="empty-state">
        {{ t('invite.noNotifications') }}
      </div>
      
      <div v-else class="invites-list">
        <div v-for="invite in invitesStore.invites" :key="invite.id" class="invite-item">
          <div class="invite-content">
            <strong>{{ invite.inviter_username }}</strong>
            {{ t('invite.invitedTo') }}
            <strong>{{ invite.campaign_name }}</strong>
          </div>
          <div class="invite-actions">
            <button @click="handleAccept(invite.id)" class="accept-btn">
              {{ t('invite.accept') }}
            </button>
            <button @click="handleReject(invite.id)" class="reject-btn">
              {{ t('invite.reject') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useInvitesStore } from '../stores/invites'
import { useCampaignsStore } from '../stores/campaigns'

const { t } = useI18n()
const invitesStore = useInvitesStore()
const campaignsStore = useCampaignsStore()

const showDropdown = ref(false)

function toggleDropdown() {
  showDropdown.value = !showDropdown.value
}

async function handleAccept(inviteId) {
  const result = await invitesStore.acceptInvite(inviteId)
  if (result.success) {
    // Add campaign to shared campaigns
    campaignsStore.addSharedCampaign(result.campaign)
  }
}

async function handleReject(inviteId) {
  await invitesStore.rejectInvite(inviteId)
}

function handleClickOutside(event) {
  const dropdown = document.querySelector('.notification-bell')
  if (dropdown && !dropdown.contains(event.target)) {
    showDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.notification-bell {
  position: relative;
}

.bell-button {
  position: relative;
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  transition: background-color 0.2s;
}

.bell-button:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.bell-button.has-notifications {
  animation: ring 2s ease-in-out infinite;
}

@keyframes ring {
  0%, 100% { transform: rotate(0deg); }
  10%, 30% { transform: rotate(-10deg); }
  20%, 40% { transform: rotate(10deg); }
}

.badge {
  position: absolute;
  top: 0;
  right: 0;
  background-color: #ff4444;
  color: white;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: bold;
}

.dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 0.5rem;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  min-width: 350px;
  max-width: 400px;
  max-height: 500px;
  overflow-y: auto;
  z-index: 1000;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.dropdown-header h3 {
  margin: 0;
  font-size: 1.1rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.loading, .empty-state {
  padding: 2rem;
  text-align: center;
  color: var(--text-secondary);
}

.invites-list {
  padding: 0.5rem;
}

.invite-item {
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.invite-item:last-child {
  border-bottom: none;
}

.invite-content {
  margin-bottom: 0.75rem;
  line-height: 1.5;
}

.invite-actions {
  display: flex;
  gap: 0.5rem;
}

.accept-btn, .reject-btn {
  flex: 1;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.accept-btn {
  background-color: #4CAF50;
  color: white;
}

.accept-btn:hover {
  background-color: #45a049;
}

.reject-btn {
  background-color: #f44336;
  color: white;
}

.reject-btn:hover {
  background-color: #da190b;
}
</style>
