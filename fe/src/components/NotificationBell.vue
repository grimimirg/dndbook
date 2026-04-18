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
