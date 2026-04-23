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
        <span
            @click.stop="openInviteModal(campaign.id)"
            class="invite-btn btn-circle btn-circle-sm"
            :title="t('campaign.inviteTooltip')"
        >
          +
        </span>
      </div>

      <div v-if="expandedCampaignId === campaign.id" class="posts-list">
        <div
            v-for="post in getCampaignPosts(campaign.id)"
            :key="post.id"
            class="post-item"
            @click="scrollToPost(post.id)"
        >
          {{ post.title }}
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
  }
});

const emit = defineEmits(['toggle-campaign', 'open-invite-modal', 'scroll-to-post']);

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
</script>
