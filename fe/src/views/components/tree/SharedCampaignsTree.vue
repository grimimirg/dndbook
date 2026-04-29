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
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../../stores/campaigns.store.js';
import {usePostsStore} from '../../../stores/posts.store.js';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();

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

const emit = defineEmits(['toggle-campaign', 'scroll-to-post']);

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
