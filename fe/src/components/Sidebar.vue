<template>
  <div class="sidebar">
    <div class="sidebar-header">
      <h2>{{ t('campaign.campaigns') }}</h2>
      <button @click="showCreateModal = true" class="primary">+ {{ t('campaign.new') }}</button>
    </div>
    
    <div v-if="campaignsStore.loading" class="loading">{{ t('common.loading') }}</div>
    
    <div v-else class="campaigns-tree">
      <div 
        v-for="campaign in campaignsStore.campaigns" 
        :key="campaign.id"
        class="campaign-node"
      >
        <div 
          class="campaign-header"
          :class="{ active: campaignsStore.currentCampaign?.id === campaign.id }"
          @click="toggleCampaign(campaign)"
        >
          <span class="expand-icon">{{ expandedCampaigns[campaign.id] ? '▼' : '▶' }}</span>
          <span class="campaign-name">{{ campaign.name }}</span>
        </div>
        
        <div v-if="expandedCampaigns[campaign.id]" class="posts-list">
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
    
    <div v-if="showCreateModal" class="modal" @click.self="showCreateModal = false">
      <div class="modal-content">
        <h3>{{ t('campaign.create') }}</h3>
        <form @submit.prevent="handleCreateCampaign">
          <div class="form-group">
            <input v-model="newCampaignName" :placeholder="t('campaign.name')" required />
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
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { useCampaignsStore } from '../stores/campaigns'
import { usePostsStore } from '../stores/posts'

const { t } = useI18n()
const campaignsStore = useCampaignsStore()
const postsStore = usePostsStore()

const expandedCampaigns = ref({})
const showCreateModal = ref(false)
const newCampaignName = ref('')
const newCampaignDescription = ref('')

async function toggleCampaign(campaign) {
  campaignsStore.setCurrentCampaign(campaign)
  expandedCampaigns.value[campaign.id] = !expandedCampaigns.value[campaign.id]
  
  if (expandedCampaigns.value[campaign.id]) {
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
    element.scrollIntoView({ behavior: 'smooth', block: 'center' })
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
</script>

<style scoped>
.sidebar {
  background: white;
  border-radius: 8px;
  padding: 16px;
  height: fit-content;
  position: sticky;
  top: 80px;
}

.sidebar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.sidebar-header h2 {
  font-size: 18px;
}

.campaigns-tree {
  max-height: 600px;
  overflow-y: auto;
}

.campaign-node {
  margin-bottom: 8px;
}

.campaign-header {
  padding: 8px;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.campaign-header:hover {
  background-color: #f0f2f5;
}

.campaign-header.active {
  background-color: #e7f3ff;
}

.expand-icon {
  font-size: 12px;
  width: 16px;
}

.campaign-name {
  font-weight: 600;
}

.posts-list {
  margin-left: 24px;
  margin-top: 4px;
}

.post-item {
  padding: 6px 8px;
  cursor: pointer;
  border-radius: 4px;
  font-size: 14px;
  color: #65676b;
}

.post-item:hover {
  background-color: #f0f2f5;
}

.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.modal-content h3 {
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #65676b;
}
</style>
