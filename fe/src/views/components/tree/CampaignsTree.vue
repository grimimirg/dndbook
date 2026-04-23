<template>
  <div class="sidebar">
    <div class="sidebar-header flex-between">
      <h2>{{ t('campaign.campaigns') }}</h2>
      <button @click="showCreateModal = true" class="primary" :title="t('campaign.newTooltip')">+ {{
          t('campaign.new')
        }}
      </button>
    </div>

    <div v-if="campaignsStore.loading" class="loading">{{ t('common.loading') }}</div>

    <div v-else class="campaigns-tree">
      <OwnedCampaignsTree
          :expanded-campaign-id="expandedCampaignId"
          @toggle-campaign="toggleCampaign"
          @open-invite-modal="openInviteModal"
          @scroll-to-post="scrollToPost"
      />

      <SharedCampaignsTree
          :expanded-campaign-id="expandedCampaignId"
          @toggle-campaign="toggleCampaign"
          @scroll-to-post="scrollToPost"
      />
    </div>

    <CampaignCreationModal
        :show="showCreateModal"
        @close="showCreateModal = false"
        @create="handleCreateCampaign"
    />

    <InviteUsersModal
        :show="showInviteModal"
        :campaign-id="selectedCampaignId"
        @close="showInviteModal = false"
        @success="handleInviteSuccess"
    />
  </div>
</template>

<script setup>
import {ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../../stores/campaigns.store.js';
import {usePostsStore} from '../../../stores/posts.store.js';
import InviteUsersModal from '../modals/InviteUsersModal.vue';
import CampaignCreationModal from '../modals/CampaignCreationModal.vue';
import OwnedCampaignsTree from './OwnedCampaignsTree.vue';
import SharedCampaignsTree from './SharedCampaignsTree.vue';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();

const expandedCampaignId = ref(null);
const showCreateModal = ref(false);
const showInviteModal = ref(false);
const selectedCampaignId = ref(null);

async function toggleCampaign(campaign) {
  if (expandedCampaignId.value !== campaign.id) {
    expandedCampaignId.value = campaign.id;
    campaignsStore.setCurrentCampaign(campaign);
    postsStore.resetSort();
    await postsStore.fetchPosts(campaign.id);
  }
}

function getCampaignPosts(campaignId) {
  if (campaignsStore.currentCampaign?.id === campaignId) {
    return postsStore.posts;
  }
  return [];
}

function scrollToPost(postId) {
  const element = document.getElementById(`post-${postId}`);
  if (element) {
    element.scrollIntoView({behavior: 'smooth', block: 'center'});
  }
}

async function handleCreateCampaign({name, description}) {
  const result = await campaignsStore.createCampaign(name, description);

  if (result.success) {
    showCreateModal.value = false;
  }
}

function openInviteModal(campaignId) {
  selectedCampaignId.value = campaignId;
  showInviteModal.value = true;
}

const emit = defineEmits(['invites-sent']);

function handleInviteSuccess() {
  console.log('Invites sent successfully');
  emit('invites-sent');
}
</script>
