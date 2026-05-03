<template>
  <div v-if="campaignsStore.ownedCampaigns.length > 0" class="campaign-group">
    <h3 class="group-title">{{ t('campaign.myCampaigns') }}</h3>
    <div
        v-for="campaign in campaignsStore.ownedCampaigns"
        :key="campaign.id"
        class="campaign-node"
    >
      <div
          class="campaign-header flex-align-center"
          :class="{ active: campaignsStore.currentCampaign?.id === campaign.id }"
          @click="toggleCampaign(campaign)"
      >
        <span class="expand-icon">{{ expandedCampaignId === campaign.id ? '▼' : '▶' }}</span>
        <span class="campaign-name">{{ campaign.name }}</span>
        <div class="campaign-menu-container">
          <button
              :ref="el => setButtonRef(campaign.id, el)"
              @click.stop="toggleCampaignMenu(campaign.id, $event)"
              class="menu-toggle-btn"
              :title="t('campaign.actions')"
          >
            ⋮
          </button>
          <Teleport to="body">
            <div
                v-if="openMenuId === campaign.id"
                class="campaign-actions-menu"
                :style="menuPosition"
            >
              <button @click.stop="handleInvite(campaign.id)" class="menu-item">
                <span class="menu-icon">+</span>
                <span>{{ t('campaign.inviteUsers') }}</span>
              </button>
              <button @click.stop="handleExport(campaign.id)" class="menu-item">
                <span class="menu-icon">⬇</span>
                <span>{{ t('campaign.export') }}</span>
              </button>
            </div>
          </Teleport>
        </div>
      </div>

      <div v-if="expandedCampaignId === campaign.id" class="posts-list">
        <div
            v-for="post in getCampaignPosts(campaign.id)"
            :key="post.id"
            class="post-item flex-align-center"
            @click="scrollToPost(post.id)"
        >
          <span v-if="!isOwner && !viewedPostIds.has(post.id)" class="checkmark-icon">✓</span>
          <span class="post-title">{{ post.title }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, onUnmounted, ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../../../stores/campaigns.store.js';
import {usePostsStore} from '../../../../stores/posts.store.js';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();
const openMenuId = ref(null);
const menuPosition = ref({});
const buttonRefs = ref({});

const props = defineProps({
  expandedCampaignId: {
    type: Number,
    default: null
  },
  viewedPostIds: {
    type: Set,
    default: () => new Set()
  },
  isOwner: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['toggle-campaign', 'open-invite-modal', 'open-export-modal', 'scroll-to-post']);

async function toggleCampaign(campaign) {
  emit('toggle-campaign', campaign);
}

function getCampaignPosts(campaignId) {
  if (campaignsStore.currentCampaign?.id === campaignId) {
    return postsStore.posts;
  }
  return [];
}

function scrollToPost(postId) {
  emit('scroll-to-post', postId);
}

function openInviteModal(campaignId) {
  emit('open-invite-modal', campaignId);
}

function openExportModal(campaignId) {
  emit('open-export-modal', campaignId);
}

function setButtonRef(campaignId, el) {
  if (el) {
    buttonRefs.value[campaignId] = el;
  }
}

function toggleCampaignMenu(campaignId, event) {
  if (openMenuId.value === campaignId) {
    openMenuId.value = null;
    menuPosition.value = {};
  } else {
    openMenuId.value = campaignId;
    const button = event.currentTarget;
    const rect = button.getBoundingClientRect();

    const menuWidth = 200;
    const top = rect.bottom + 8;
    const left = rect.right - menuWidth;

    menuPosition.value = {
      top: `${top}px`,
      left: `${left}px`,
      right: 'auto'
    };
  }
}

function handleInvite(campaignId) {
  openMenuId.value = null;
  openInviteModal(campaignId);
}

function handleExport(campaignId) {
  openMenuId.value = null;
  openExportModal(campaignId);
}

function handleClickOutside(event) {
  const menuContainer = event.target.closest('.campaign-menu-container');
  if (!menuContainer && openMenuId.value !== null) {
    openMenuId.value = null;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.checkmark-icon {
  color: var(--success-color, #4caf50);
  font-weight: bold;
  font-size: 1em;
  margin-right: 8px;
}

.post-title {
  flex: 1;
}
</style>
