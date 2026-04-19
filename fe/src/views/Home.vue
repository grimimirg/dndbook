<template>
  <div class="home">
    <header class="header">
      <div class="header-content">
        <h1>{{ t('app.title') }}</h1>
        <div class="user-info">
          <span>{{ authStore.user?.username }}</span>
          <NotificationBell/>
          <button @click="handleLogout" class="secondary">{{ t('auth.logout') }}</button>
          <LanguageSelector/>
          <ThemeToggle/>
        </div>
      </div>
    </header>

    <div class="main-content">
      <CampaignDescriptionPanel/>

      <div class="feed">
        <div class="sort-controls">
          <span class="sort-label">{{ t('sort.label') }}:</span>
          <button
              @click="changeSortBy('created')"
              :class="{ primary: postsStore.sortBy === 'created', secondary: postsStore.sortBy !== 'created' }"
          >
            {{ t('sort.byCreated') }}
            <span v-if="postsStore.sortBy === 'created'">{{ postsStore.sortDirection === 'desc' ? ' ↓' : ' ↑' }}</span>
          </button>
          <button
              @click="changeSortBy('updated')"
              :class="{ primary: postsStore.sortBy === 'updated', secondary: postsStore.sortBy !== 'updated' }"
          >
            {{ t('sort.byUpdated') }}
          </button>
        </div>

        <PostCreator v-if="isCurrentCampaignOwned"/>

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

      <Sidebar/>
    </div>

    <InviteToast/>
  </div>
</template>

<script setup>
import {computed, onMounted, onUnmounted, ref} from 'vue';
import {useRouter} from 'vue-router';
import {useI18n} from 'vue-i18n';
import {useAuthStore} from '../stores/auth.store.js';
import {useCampaignsStore} from '../stores/campaigns.store.js';
import {usePostsStore} from '../stores/posts.store.js';
import {useInvitesStore} from '../stores/invites.store.js';
import socketService from '../services/socket.service.js';
import Sidebar from './components/Sidebar.vue';
import PostCard from './components/PostCard.vue';
import PostCreator from './components/PostCreator.vue';
import LanguageSelector from './components/LanguageSelector.vue';
import ThemeToggle from './components/ThemeToggle.vue';
import NotificationBell from './components/NotificationBell.vue';
import InviteToast from './components/InviteToast.vue';
import CampaignDescriptionPanel from './components/CampaignDescriptionPanel.vue';

const router = useRouter();
const {t} = useI18n();
const authStore = useAuthStore();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();
const invitesStore = useInvitesStore();

const postRefs = ref({});

const isCurrentCampaignOwned = computed(() => {
  if (!campaignsStore.currentCampaign) return false;
  return campaignsStore.ownedCampaigns.some(
      campaign => campaign.id === campaignsStore.currentCampaign.id
  );
});

function setPostRef(postId, el) {
  if (el) {
    postRefs.value[postId] = el;
  }
}

onMounted(async () => {
  await campaignsStore.fetchCampaigns();
  await invitesStore.fetchInvites();

  // Initialize Socket.IO
  const token = localStorage.getItem('token');
  if (token) {
    socketService.connect(token);
    invitesStore.setupSocketListener();
  }
});

onUnmounted(() => {
  socketService.disconnect();
});

function handleLogout() {
  authStore.logout();
  router.push('/login');
}

async function changeSortBy(sort) {
  postsStore.setSortBy(sort);
  if (campaignsStore.currentCampaign) {
    await postsStore.fetchPosts(campaignsStore.currentCampaign.id);
  }
}

async function loadMore() {
  if (campaignsStore.currentCampaign && postsStore.hasMore) {
    await postsStore.fetchPosts(
        campaignsStore.currentCampaign.id,
        postsStore.currentPage + 1,
        true
    );
  }
}
</script>
