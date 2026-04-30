<template>
  <div class="sidebar">
    <div class="sidebar-header flex-between">
      <h2>{{ t('campaign.campaigns') }}</h2>
      <div class="campaign-menu-container">
        <button 
            ref="actionsMenuButton"
            @click="toggleActionsMenu" 
            class="menu-toggle-btn" 
            :title="t('campaign.actions')"
        >
          ⋮
        </button>
        <Teleport to="body">
          <div v-if="showActionsMenu" class="campaign-actions-menu" :style="menuPosition">
            <button @click="handleNewCampaign" class="menu-item">
              <span class="menu-icon">+</span>
              <span>{{ t('campaign.new') }}</span>
            </button>
            <button @click="handleImportCampaign" class="menu-item">
              <span class="menu-icon">⬆</span>
              <span>{{ t('campaign.import') }}</span>
            </button>
          </div>
        </Teleport>
      </div>
    </div>

    <div v-if="campaignsStore.loading" class="loading">{{ t('common.loading') }}</div>

    <div v-else class="campaigns-tree">
      <OwnedCampaignsTree
          :expanded-campaign-id="expandedCampaignId"
          :viewed-post-ids="props.viewedPostIds"
          :is-owner="props.isOwner"
          @toggle-campaign="toggleCampaign"
          @open-invite-modal="openInviteModal"
          @open-export-modal="openExportModal"
          @scroll-to-post="scrollToPost"
      />

      <SharedCampaignsTree
          :expanded-campaign-id="expandedCampaignId"
          :viewed-post-ids="props.viewedPostIds"
          :is-owner="props.isOwner"
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

    <CampaignImportModal
        :show="showImportModal"
        @close="showImportModal = false"
        @success="handleImportSuccess"
    />

    <ConfirmModal
        :show="showExportConfirm"
        :title="t('campaign.exportTitle')"
        :message="t('campaign.confirmExport')"
        @confirm="handleExportConfirm"
        @cancel="showExportConfirm = false"
    />
  </div>
</template>

<script setup>
import {ref, onMounted, onUnmounted} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../../stores/campaigns.store.js';
import {usePostsStore} from '../../../stores/posts.store.js';
import InviteUsersModal from '../modals/InviteUsersModal.vue';
import CampaignCreationModal from '../modals/CampaignCreationModal.vue';
import CampaignImportModal from '../modals/CampaignImportModal.vue';
import ConfirmModal from '../modals/ConfirmModal.vue';
import OwnedCampaignsTree from './OwnedCampaignsTree.vue';
import SharedCampaignsTree from './SharedCampaignsTree.vue';
import axios from 'axios';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();

const expandedCampaignId = ref(null);
const showCreateModal = ref(false);
const showInviteModal = ref(false);
const showImportModal = ref(false);
const showExportConfirm = ref(false);
const selectedCampaignId = ref(null);
const showActionsMenu = ref(false);
const menuPosition = ref({});
const actionsMenuButton = ref(null);

const props = defineProps({
  viewedPostIds: {
    type: Set,
    default: () => new Set()
  },
  isOwner: {
    type: Boolean,
    default: false
  }
});

function toggleActionsMenu() {
  if (showActionsMenu.value) {
    showActionsMenu.value = false;
    menuPosition.value = {};
  } else {
    showActionsMenu.value = true;
    const button = actionsMenuButton.value;
    if (button) {
      const rect = button.getBoundingClientRect();
      const menuWidth = 200;
      const viewportWidth = window.innerWidth;
      
      let left = rect.right - menuWidth;
      
      if (left < 8) {
        left = 8;
      }
      
      if (left + menuWidth > viewportWidth - 8) {
        left = viewportWidth - menuWidth - 8;
      }
      
      const top = rect.bottom + 8;
      
      menuPosition.value = {
        top: `${top}px`,
        left: `${left}px`,
        right: 'auto'
      };
    }
  }
}

function handleNewCampaign() {
  showActionsMenu.value = false;
  showCreateModal.value = true;
}

function handleImportCampaign() {
  showActionsMenu.value = false;
  showImportModal.value = true;
}

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

function openExportModal(campaignId) {
  selectedCampaignId.value = campaignId;
  showExportConfirm.value = true;
}

async function handleExportConfirm() {
  showExportConfirm.value = false;
  
  try {
    const token = localStorage.getItem('token');
    const response = await axios.get(
      `${import.meta.env.VITE_API_URL}/api/export/${selectedCampaignId.value}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        },
        responseType: 'blob'
      }
    );
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    const contentDisposition = response.headers['content-disposition'];
    let filename = 'campaign_export.zip';
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1];
      }
    }
    
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Export error:', error);
    alert(t('campaign.exportError'));
  }
}

async function handleImportSuccess(data) {
  console.log('Campaign imported successfully:', data);
  await campaignsStore.fetchCampaigns();
  showImportModal.value = false;
}

function handleClickOutside(event) {
  const menuContainer = event.target.closest('.campaign-menu-container');
  if (!menuContainer && showActionsMenu.value) {
    showActionsMenu.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
