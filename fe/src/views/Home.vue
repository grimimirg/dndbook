<template>
  <div class="home">
    <header class="header">
      <div class="header-content">
        <h1>{{ t('app.title') }}</h1>
        <div class="user-info">
          <select v-model="currentLocale" @change="changeLocale" class="language-selector">
            <option value="en">English</option>
            <option value="it">Italiano</option>
            <option value="de">Deutsch</option>
          </select>
          <span>{{ authStore.user?.username }}</span>
          <button @click="handleLogout" class="secondary">{{ t('auth.logout') }}</button>
        </div>
      </div>
    </header>
    
    <div class="main-content">
      <div class="feed">
        <div class="sort-controls">
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

const router = useRouter()
const { locale, t } = useI18n()
const authStore = useAuthStore()
const campaignsStore = useCampaignsStore()
const postsStore = usePostsStore()

const postRefs = ref({})
const currentLocale = ref(locale.value)

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

function changeLocale() {
  locale.value = currentLocale.value
  localStorage.setItem('locale', currentLocale.value)
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

<style scoped>
.home {
  min-height: 100vh;
  background-color: #f0f2f5;
}

.header {
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 16px 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header h1 {
  font-size: 24px;
  color: #1877f2;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.language-selector {
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  background: white;
}

.language-selector:focus {
  outline: none;
  border-color: #1877f2;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 20px;
}

.feed {
  max-width: 680px;
}

.sort-controls {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}

.loading, .empty-state {
  text-align: center;
  padding: 40px;
  color: #65676b;
}

.load-more {
  text-align: center;
  margin-top: 16px;
}

.load-more button {
  width: 100%;
}
</style>
