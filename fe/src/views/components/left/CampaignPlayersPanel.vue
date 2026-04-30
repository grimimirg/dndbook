<template>
  <div class="campaign-players-panel card flex-col">
    <div v-if="campaignsStore.currentCampaign">
      <div class="panel-header flex-between" @click="toggleCollapse">
        <h3>{{ t('campaign.players') }}</h3>
        <span class="toggle-icon" :class="{ collapsed: isCollapsed }">
          {{ isCollapsed ? '▶' : '▼' }}
        </span>
      </div>

      <transition name="collapse">
        <div v-show="!isCollapsed" class="panel-content">
        <div v-if="loading" class="loading flex-center">
          {{ t('common.loading') }}
        </div>

        <div v-else>
          <div class="players-section">
            <h4 class="section-label">{{ t('campaign.players') }}</h4>
            <div v-if="members.length === 0" class="empty-message">
              <p>{{ t('campaign.noPlayers') }}</p><br>
              <p class="hint">{{ t('campaign.noPlayersHint') }}</p>
            </div>
            <div v-else class="players-list flex-col">
              <div v-for="member in members" :key="member.id" class="player-item flex-between">
                <span class="player-name">{{ member.username }}</span>
                <button
                    v-if="isCurrentCampaignOwned"
                    @click="handleRemoveMember(member)"
                    class="remove-btn btn-circle btn-circle-sm"
                    :title="t('campaign.removePlayer')"
                >
                  ×
                </button>
              </div>
            </div>
          </div>

          <div v-if="isCurrentCampaignOwned" class="invites-section">
            <h4 class="section-label">{{ t('campaign.invitedPlayers') }}</h4>
            <div v-if="pendingInvites.length === 0" class="empty-message">
              {{ t('campaign.noInvitedPlayers') }}
            </div>
            <div v-else class="players-list flex-col">
              <div v-for="invite in pendingInvites" :key="invite.id" class="player-item pending flex-between">
                <span class="player-name">{{ invite.invitee_username }}</span>
                <button
                    @click="handleCancelInvite(invite)"
                    class="remove-btn btn-circle btn-circle-sm"
                    :title="t('campaign.cancelInvite')"
                >
                  ×
                </button>
              </div>
            </div>
          </div>
        </div>
        </div>
      </transition>
    </div>

    <ConfirmModal
      :show="showRemoveMemberConfirm"
      :title="t('campaign.removePlayerTitle')"
      :message="t('campaign.confirmRemovePlayer')"
      @confirm="confirmRemoveMember"
      @cancel="cancelRemoveMember"
    />

    <ConfirmModal
      :show="showCancelInviteConfirm"
      :title="t('campaign.cancelInviteTitle')"
      :message="t('campaign.confirmCancelInvite')"
      @confirm="confirmCancelInvite"
      @cancel="cancelCancelInvite"
    />
  </div>
</template>

<script setup>
import {computed, onMounted, ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../../stores/campaigns.store.js';
import {useAuthStore} from '../../../stores/auth.store.js';
import api from '../../../services/api.service.js';
import ConfirmModal from '../modals/ConfirmModal.vue';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const authStore = useAuthStore();

const members = ref([]);
const pendingInvites = ref([]);
const loading = ref(false);
const showRemoveMemberConfirm = ref(false);
const showCancelInviteConfirm = ref(false);
const memberToRemove = ref(null);
const inviteToCancel = ref(null);
const isCollapsed = ref(true);

const isCurrentCampaignOwned = computed(() => {
  if (!campaignsStore.currentCampaign) return false;
  return campaignsStore.ownedCampaigns.some(
      campaign => campaign.id === campaignsStore.currentCampaign.id
  );
});

async function fetchMembers() {
  if (!campaignsStore.currentCampaign) {
    members.value = [];
    pendingInvites.value = [];
    return;
  }

  loading.value = true;
  try {
    const response = await api.get(`/campaigns/${campaignsStore.currentCampaign.id}/members`);
    members.value = response.data.members || [];
    pendingInvites.value = response.data.pending_invites || [];
  } catch (error) {
    console.error('Failed to fetch campaign members:', error);
  } finally {
    loading.value = false;
  }
}

function handleRemoveMember(member) {
  memberToRemove.value = member;
  showRemoveMemberConfirm.value = true;
}

async function confirmRemoveMember() {
  showRemoveMemberConfirm.value = false;
  try {
    await api.delete(`/campaigns/${campaignsStore.currentCampaign.id}/members/${memberToRemove.value.id}`);
    await fetchMembers();
  } catch (error) {
    alert(error.response?.data?.error || t('common.error'));
  }
  memberToRemove.value = null;
}

function cancelRemoveMember() {
  showRemoveMemberConfirm.value = false;
  memberToRemove.value = null;
}

function handleCancelInvite(invite) {
  inviteToCancel.value = invite;
  showCancelInviteConfirm.value = true;
}

async function confirmCancelInvite() {
  showCancelInviteConfirm.value = false;
  try {
    await api.delete(`/campaigns/${campaignsStore.currentCampaign.id}/invites/${inviteToCancel.value.id}`);
    await fetchMembers();
  } catch (error) {
    alert(error.response?.data?.error || t('common.error'));
  }
  inviteToCancel.value = null;
}

function cancelCancelInvite() {
  showCancelInviteConfirm.value = false;
  inviteToCancel.value = null;
}

function toggleCollapse() {
  isCollapsed.value = !isCollapsed.value;
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
