<template>
  <div v-if="campaignsStore.sharedCampaigns.length > 0" class="campaign-group">
    <h3 class="group-title">{{ t('campaign.sharedCampaigns') }}</h3>
    <div
        v-for="campaign in campaignsStore.sharedCampaigns"
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
          :style="menuPosition"
      >
        <button @click="handleEditPost" class="menu-item">
          <span>{{ t('post.edit') }}</span>
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
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

const emit = defineEmits(['toggle-campaign', 'scroll-to-post', 'edit-post']);
const {openMenuPostId, menuPosition, togglePostMenu, handleEditPost} = usePostActionsMenu(emit);

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

async function handlePostReorder() {
  await postsStore.reorderPosts();
}
</script>
