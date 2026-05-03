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
        <draggable
            v-if="campaignsStore.currentCampaign?.id === campaign.id && isOwner && postsStore.sortBy === 'custom'"
            v-model="postsStore.posts"
            item-key="id"
            :delay="500"
            :delay-on-touch-only="true"
            @end="handlePostReorder"
            class="draggable-posts"
            :style="{ gap: '0' }"
            tag="div"
        >
          <template #item="{element: post}">
            <PostItemTree
                :post="post"
                :is-owner="isOwner"
                :viewed-post-ids="viewedPostIds"
                @scroll-to-post="scrollToPost"
                @toggle-post-menu="togglePostMenu"
            />
          </template>
        </draggable>
        <div v-else class="non-draggable-posts">
          <PostItemTree
              v-for="post in getCampaignPosts(campaign.id)"
              :key="post.id"
              :post="post"
              :is-owner="isOwner"
              :viewed-post-ids="viewedPostIds"
              @scroll-to-post="scrollToPost"
              @toggle-post-menu="togglePostMenu"
          />
        </div>
      </div>
    </div>
    <Teleport to="body">
      <div
          v-if="openMenuPostId"
          class="post-actions-menu"
          :style="postMenuPosition"
      >
        <button @click="handleEditPost" class="menu-item">
          <span>{{ t('post.edit') }}</span>
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import {onMounted, onUnmounted, ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../../../stores/campaigns.store.js';
import {usePostsStore} from '../../../../stores/posts.store.js';
import {usePermissionsStore} from '../../../../stores/permissions.store.js';
import draggable from 'vuedraggable';
import {usePostActionsMenu} from '../../../../composables/usePostActionsMenu.js';
import PostItemTree from './PostItemTree.vue';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();
const permissionsStore = usePermissionsStore();
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

const emit = defineEmits(['toggle-campaign', 'open-invite-modal', 'open-export-modal', 'scroll-to-post', 'edit-post']);
const {openMenuPostId, menuPosition: postMenuPosition, togglePostMenu, handleEditPost} = usePostActionsMenu(emit);

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

async function handlePostReorder() {
  await postsStore.reorderPosts();
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
