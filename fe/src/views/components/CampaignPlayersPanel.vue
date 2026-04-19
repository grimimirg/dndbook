<template>
  <div class="campaign-players-panel card">
    <div v-if="campaignsStore.currentCampaign && isCurrentCampaignOwned">

      <div class="panel-content">
        <div v-if="loading" class="loading">
          {{ t('common.loading') }}
        </div>

        <div v-else>
          <div class="players-section">
            <h4 class="section-label">{{ t('campaign.players') }}</h4>
            <div v-if="members.length === 0" class="empty-message">
              {{ t('campaign.noPlayers') }}
            </div>
            <div v-else class="players-list">
              <div v-for="member in members" :key="member.id" class="player-item">
                <span class="player-name">{{ member.username }}</span>
                <button
                    @click="handleRemoveMember(member)"
                    class="remove-btn"
                    :title="t('campaign.removePlayer')"
                >
                  ×
                </button>
              </div>
            </div>
          </div>

          <div class="invites-section">
            <h4 class="section-label">{{ t('campaign.invitedPlayers') }}</h4>
            <div v-if="pendingInvites.length === 0" class="empty-message">
              {{ t('campaign.noInvitedPlayers') }}
            </div>
            <div v-else class="players-list">
              <div v-for="invite in pendingInvites" :key="invite.id" class="player-item pending">
                <span class="player-name">{{ invite.invitee_username }}</span>
                <button
                    @click="handleCancelInvite(invite)"
                    class="remove-btn"
                    :title="t('campaign.cancelInvite')"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../stores/campaigns.store.js';
import {useAuthStore} from '../../stores/auth.store.js';
import api from '../../services/api.service.js';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const authStore = useAuthStore();

const members = ref([]);
const pendingInvites = ref([]);
const loading = ref(false);

const isCurrentCampaignOwned = computed(() => {
  if (!campaignsStore.currentCampaign) return false;
  return campaignsStore.ownedCampaigns.some(
      campaign => campaign.id === campaignsStore.currentCampaign.id
  );
});

async function fetchMembers() {
  if (!campaignsStore.currentCampaign || !isCurrentCampaignOwned.value) {
    members.value = [];
    pendingInvites.value = [];
    return;
  }

  loading.value = true;
  try {
    const response = await api.get(`/api/campaigns/${campaignsStore.currentCampaign.id}/members`);
    members.value = response.data.members || [];
    pendingInvites.value = response.data.pending_invites || [];
  } catch (error) {
    console.error('Failed to fetch campaign members:', error);
  } finally {
    loading.value = false;
  }
}

async function handleRemoveMember(member) {
  if (!confirm(t('campaign.confirmRemovePlayer'))) {
    return;
  }

  try {
    await api.delete(`/api/campaigns/${campaignsStore.currentCampaign.id}/members/${member.id}`);
    await fetchMembers();
  } catch (error) {
    alert(error.response?.data?.error || t('common.error'));
  }
}

async function handleCancelInvite(invite) {
  if (!confirm(t('campaign.confirmCancelInvite'))) {
    return;
  }

  try {
    await api.delete(`/api/campaigns/${campaignsStore.currentCampaign.id}/invites/${invite.id}`);
    await fetchMembers();
  } catch (error) {
    alert(error.response?.data?.error || t('common.error'));
  }
}

watch(() => campaignsStore.currentCampaign, () => {
  fetchMembers();
}, {immediate: true});

onMounted(() => {
  fetchMembers();
});

defineExpose({
  fetchMembers
});
</script>

<style scoped>
.campaign-players-panel {
  margin-bottom: 1rem;
}

.panel-content {
  padding: 1rem;
}

.loading {
  text-align: center;
  padding: 1rem;
  color: var(--text-secondary);
}

.players-section,
.invites-section {
  margin-bottom: 1.5rem;
}

.invites-section {
  margin-bottom: 0;
}

.section-label {
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}

.empty-message {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-style: italic;
}

.players-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.player-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: var(--bg-secondary);
  border-radius: 4px;
  transition: background 0.2s;
}

.player-item:hover {
  background: var(--bg-hover);
}

.player-item.pending {
  opacity: 0.7;
}

.player-name {
  font-size: 0.9rem;
  color: var(--text-primary);
}

.remove-btn {
  background: none;
  border: none;
  color: var(--danger);
  font-size: 1.5rem;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background 0.2s;
}

.remove-btn:hover {
  background: var(--danger-light);
}
</style>
