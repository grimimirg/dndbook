<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h2>{{ t('campaign.campaigns') }}</h2>
      <button @click="showCreateModal = true" class="primary">+ {{ t('campaign.new') }}</button>
    </div>

    <div v-if="campaignsStore.loading" class="loading">{{ t('common.loading') }}</div>

    <div v-else class="campaigns-tree">
      <!-- Owned Campaigns -->
      <div v-if="campaignsStore.ownedCampaigns.length > 0" class="campaign-group">
        <h3 class="group-title">{{ t('campaign.myCampaigns') }}</h3>
        <div
            v-for="campaign in campaignsStore.ownedCampaigns"
            :key="campaign.id"
            class="campaign-node"
        >
          <div
              class="campaign-header"
              :class="{ active: campaignsStore.currentCampaign?.id === campaign.id }"
              @click="toggleCampaign(campaign)"
          >
            <span class="expand-icon">{{ expandedCampaignId === campaign.id ? '▼' : '▶' }}</span>
            <span class="campaign-name">{{ campaign.name }}</span>
            <button
                @click.stop="openInviteModal(campaign.id)"
                class="invite-btn"
                :title="t('campaign.inviteTooltip')"
            >
              +
            </button>
            <button
                @click.stop="deleteCampaign(campaign.id)"
                class="delete-btn"
                :title="t('campaign.deleteTooltip')"
            >
              -
            </button>
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

      <!-- Shared Campaigns -->
      <div v-if="campaignsStore.sharedCampaigns.length > 0" class="campaign-group">
        <h3 class="group-title">{{ t('campaign.sharedCampaigns') }}</h3>
        <div
            v-for="campaign in campaignsStore.sharedCampaigns"
            :key="campaign.id"
            class="campaign-node"
        >
          <div
              class="campaign-header"
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
                class="post-item"
                @click="scrollToPost(post.id)"
            >
              {{ post.title }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-if="showCreateModal" class="modal" @click.self="showCreateModal = false">
      <div class="modal-content">
        <h3>{{ t('campaign.create') }}</h3>
        <form @submit.prevent="handleCreateCampaign">
          <div class="form-group">
            <input v-model="newCampaignName" :placeholder="t('campaign.name')" required/>
          </div>
          <div class="form-group">
            <textarea v-model="newCampaignDescription" :placeholder="t('campaign.description')" rows="4"></textarea>
          </div>
          <div class="modal-actions">
            <button type="button" @click="showCreateModal = false" class="secondary">{{ t('campaign.cancel') }}</button>
            <button type="submit" class="primary">{{ t('campaign.create') }}</button>
          </div>
        </form>
      </div>
    </div>

    <InviteUsersModal
        :show="showInviteModal"
        :campaign-id="selectedCampaignId"
        @close="showInviteModal = false"
        @success="handleInviteSuccess"
    />
  </div>
</template>

<script setup>
import {ref} from 'vue'
import {useI18n} from 'vue-i18n'
import {useCampaignsStore} from '../stores/campaigns'
import {usePostsStore} from '../stores/posts'
import InviteUsersModal from './InviteUsersModal.vue'

const {t} = useI18n()
const campaignsStore = useCampaignsStore()
const postsStore = usePostsStore()

const expandedCampaignId = ref(null)
const showCreateModal = ref(false)
const showInviteModal = ref(false)
const selectedCampaignId = ref(null)
const newCampaignName = ref('')
const newCampaignDescription = ref('')

async function toggleCampaign(campaign) {
  if (expandedCampaignId.value !== campaign.id) {
    expandedCampaignId.value = campaign.id
    campaignsStore.setCurrentCampaign(campaign)
    postsStore.resetSort()
    await postsStore.fetchPosts(campaign.id)
  }
}

function getCampaignPosts(campaignId) {
  if (campaignsStore.currentCampaign?.id === campaignId) {
    return postsStore.posts
  }
  return []
}

function scrollToPost(postId) {
  const element = document.getElementById(`post-${postId}`)
  if (element) {
    element.scrollIntoView({behavior: 'smooth', block: 'center'})
  }
}

async function handleCreateCampaign() {
  const result = await campaignsStore.createCampaign(
      newCampaignName.value,
      newCampaignDescription.value
  )

  if (result.success) {
    showCreateModal.value = false
    newCampaignName.value = ''
    newCampaignDescription.value = ''
  }
}

function openInviteModal(campaignId) {
  selectedCampaignId.value = campaignId
  showInviteModal.value = true
}

function handleInviteSuccess() {
  console.log('Invites sent successfully')
}

async function deleteCampaign(campaignId) {
  if (confirm(t('campaign.confirmDelete'))) {
    await campaignsStore.deleteCampaign(campaignId)
  }
}
</script>

<style scoped>
.campaign-group {
  margin-bottom: 1.5rem;
}

.group-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 0.75rem;
  padding: 0 0.5rem;
}

.campaign-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.invite-btn {
  margin-left: auto;
  background-color: var(--accent-gold-2);
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: bold;
  transition: all 0.2s;
  opacity: 0;
}

.campaign-header:hover .invite-btn {
  opacity: 1;
}

.invite-btn:hover {
  background-color: var(--accent-gold-3);
  transform: scale(1.1);
}

.delete-btn {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  font-size: 1.2rem;
  font-weight: bold;
  transition: all 0.2s;
  opacity: 0;
  margin-left: 0.25rem;
}

.campaign-header:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background-color: #c82333;
  transform: scale(1.1);
}
</style>
