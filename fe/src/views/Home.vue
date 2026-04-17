<template>
  <div class="home">
    <header class="header">
      <div class="header-content">
        <h1>{{ t('app.title') }}</h1>
        <div class="user-info">
          <span>{{ authStore.user?.username }}</span>
          <button @click="handleLogout" class="secondary">{{ t('auth.logout') }}</button>
          <LanguageSelector />
          <ThemeToggle />
        </div>
      </div>
    </header>
    
    <div class="main-content">
      <div class="feed">
        <div class="sort-controls">
          <span class="sort-label">{{ t('sort.label') }}:</span>
          <button 
            @click="changeSortBy('created')" 
            :class="{ primary: postsStore.sortBy === 'created', secondary: postsStore.sortBy !== 'created' }"
          >
            {{ t('sort.byCreated') }}
          </button>
          <button 
            @click="changeSortBy('updated')" 
            :class="{ primary: postsStore.sortBy === 'updated', secondary: postsStore.sortBy !== 'updated' }"
          >
            {{ t('sort.byUpdated') }}
          </button>
        </div>
        
        <PostCreator v-if="campaignsStore.currentCampaign" />
        
        <div v-if="postsStore.loading && postsStore.posts.length === 0" class="loading">
          {{ t('post.loading') }}
        </div>
        
        <div v-else-if="!campaignsStore.currentCampaign" class="empty-state">
          {{ t('campaign.selectCampaign') }}
        </div>
        
        <div v-else-if="postsStore.posts.length === 0" class="empty-state">
          {{ t('post.noPosts') }}
        </div>
        
        <PostCard 
          v-for="post in postsStore.posts" 
          :key="post.id" 
          :post="post"
          :ref="el => setPostRef(post.id, el)"
        />
        
        <div v-if="postsStore.hasMore && !postsStore.loading" class="load-more">
          <button @click="loadMore" class="secondary">{{ t('post.loadMore') }}</button>
        </div>
      </div>
      
      <Sidebar />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import { useCampaignsStore } from '../stores/campaigns'
import { usePostsStore } from '../stores/posts'
import Sidebar from '../components/Sidebar.vue'
import PostCard from '../components/PostCard.vue'
import PostCreator from '../components/PostCreator.vue'
import LanguageSelector from '../components/LanguageSelector.vue'
import ThemeToggle from '../components/ThemeToggle.vue'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()
const campaignsStore = useCampaignsStore()
const postsStore = usePostsStore()

const postRefs = ref({})

function setPostRef(postId, el) {
  if (el) {
    postRefs.value[postId] = el
  }
}

onMounted(async () => {
  await campaignsStore.fetchCampaigns()
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

async function changeSortBy(sort) {
  postsStore.setSortBy(sort)
  if (campaignsStore.currentCampaign) {
    await postsStore.fetchPosts(campaignsStore.currentCampaign.id)
  }
}

async function loadMore() {
  if (campaignsStore.currentCampaign && postsStore.hasMore) {
    await postsStore.fetchPosts(
      campaignsStore.currentCampaign.id, 
      postsStore.currentPage + 1, 
      true
    )
  }
}
</script>
