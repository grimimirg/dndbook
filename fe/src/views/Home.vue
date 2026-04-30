<template>
  <div class="home">
    <header class="header">
      <div class="header-content flex-align-center">
        <HamburgerMenu ref="hamburgerMenu" @invites-sent="handleInvitesSent" class="mobile-only"/>
        <h1>{{ t('app.title') }}</h1>
        <div class="user-info flex-align-center">
          <span class="username-label">{{ authStore.user?.username }}</span>
          <NotificationBell/>
          <button @click="handleLogout" class="secondary desktop-only">{{ t('auth.logout') }}</button>
          <LanguageSelector class="desktop-only"/>
          <ThemeToggle class="desktop-only"/>
        </div>
      </div>
    </header>

    <div class="main-content">
      <div class="campaign-info-column flex-col desktop-only">
        <CampaignDescriptionPanel/>
        <CampaignCharactersPanel v-if="campaignsStore.currentCampaign"/>
        <CampaignPlayersPanel v-if="campaignsStore.currentCampaign" ref="playersPanel"/>
      </div>

      <div class="feed">
        <CampaignsTree 
          :viewed-post-ids="viewedPostIds" 
          :is-owner="isCurrentCampaignOwned"
          @invites-sent="handleInvitesSent"
          class="mobile-campaigns-tree"/>
        
        <div v-if="campaignsStore.currentCampaign" class="sort-controls flex-align-center">
          <span class="sort-label">{{ t('sort.label') }}:</span>
          <button
              @click="changeSortBy('created')"
              :class="{ primary: postsStore.sortBy === 'created', secondary: postsStore.sortBy !== 'created' }"
          >
            {{ t('sort.byCreated') }}
            <span>{{ postsStore.sortDirection === 'desc' ? ' ↓' : ' ↑' }}</span>
          </button>
          <button
              @click="changeSortBy('updated')"
              :class="{ primary: postsStore.sortBy === 'updated', secondary: postsStore.sortBy !== 'updated' }"
          >
            {{ t('sort.byUpdated') }}
          </button>
          <input
              v-model="searchQuery"
              type="text"
              :placeholder="t('sort.search')"
              class="search-input"
          />
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
            v-for="post in filteredPosts"
            :key="post.id"
            :post="post"
            :is-viewed="viewedPostIds.has(post.id)"
            :is-owner="isCurrentCampaignOwned"
            :highlighted-comment-id="highlightedCommentId"
            @mark-viewed="markPostAsViewed"
            :ref="el => setPostRef(post.id, el)"
        />

        <div v-if="postsStore.hasMore && !postsStore.loading" class="load-more">
          <button @click="loadMore" class="secondary">{{ t('post.loadMore') }}</button>
        </div>
      </div>

      <CampaignsTree 
        :viewed-post-ids="viewedPostIds" 
        :is-owner="isCurrentCampaignOwned"
        @invites-sent="handleInvitesSent"
        class="desktop-only"/>
    </div>

    <InviteToast/>
  </div>
</template>

<script setup>
import {computed, onMounted, onUnmounted, ref, watch} from 'vue';
import {useRouter} from 'vue-router';
import {useI18n} from 'vue-i18n';
import {useAuthStore} from '../stores/auth.store.js';
import {useCampaignsStore} from '../stores/campaigns.store.js';
import {usePostsStore} from '../stores/posts.store.js';
import {useInvitesStore} from '../stores/invites.store.js';
import socketService from '../services/socket.service.js';
import apiService from '../services/api.service.js';
import CampaignsTree from './components/right/tree/CampaignsTree.vue';
import PostCard from './components/middle/PostCard.vue';
import PostCreator from './components/middle/PostCreator.vue';
import LanguageSelector from './components/up/LanguageSelector.vue';
import ThemeToggle from './components/up/ThemeToggle.vue';
import NotificationBell from './components/up/NotificationBell.vue';
import InviteToast from './components/InviteToast.vue';
import CampaignDescriptionPanel from './components/left/CampaignDescriptionPanel.vue';
import CampaignCharactersPanel from './components/left/characters/CampaignCharactersPanel.vue';
import CampaignPlayersPanel from './components/left/CampaignPlayersPanel.vue';
import HamburgerMenu from './components/left/HamburgerMenu.vue';

const router = useRouter();
const {t} = useI18n();
const authStore = useAuthStore();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();
const invitesStore = useInvitesStore();

const postRefs = ref({});
const playersPanel = ref(null);
const hamburgerMenu = ref(null);
const searchQuery = ref('');
const debouncedSearchQuery = ref('');
const viewedPostIds = ref(new Set());
const highlightedCommentId = ref(null);
let debounceTimeout = null;

const isCurrentCampaignOwned = computed(() => {
  if (!campaignsStore.currentCampaign) return false;
  return campaignsStore.ownedCampaigns.some(
      campaign => campaign.id === campaignsStore.currentCampaign.id
  );
});

const filteredPosts = computed(() => {
  if (!debouncedSearchQuery.value.trim()) {
    return postsStore.posts;
  }

  const query = debouncedSearchQuery.value.toLowerCase();
  return postsStore.posts.filter(post => {
    const titleMatch = post.title?.toLowerCase().includes(query);
    const contentMatch = post.content?.toLowerCase().includes(query);
    return titleMatch || contentMatch;
  });
});

watch(searchQuery, (newValue) => {
  if (debounceTimeout) {
    clearTimeout(debounceTimeout);
  }

  debounceTimeout = setTimeout(() => {
    debouncedSearchQuery.value = newValue;
  }, 500);
});

function setPostRef(postId, el) {
  if (el) {
    postRefs.value[postId] = el;
  }
}

function setupPlayerJoinedListener() {
  socketService.on('player_joined', (data) => {
    const message = t('campaign.playerJoined', {
      player: data.player_username,
      campaign: data.campaign_name
    });

    if (Notification.permission === 'granted') {
      new Notification(t('campaign.players'), {
        body: message,
        icon: '/images/dnd-book-logo.png'
      });
    }

    alert(message);

    if (playersPanel.value && campaignsStore.currentCampaign?.id === data.campaign_id) {
      playersPanel.value.fetchMembers();
    }
  });
}

function handleInvitesSent() {
  if (playersPanel.value) {
    playersPanel.value.fetchMembers();
  }
  if (hamburgerMenu.value?.playersPanel) {
    hamburgerMenu.value.playersPanel.fetchMembers();
  }
}

onMounted(async () => {
  await campaignsStore.fetchCampaigns();
  await invitesStore.fetchInvites();

  const token = localStorage.getItem('token');
  if (token) {
    socketService.connect(token);
    invitesStore.setupSocketListener();
    setupPlayerJoinedListener();
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

async function fetchViewedStatus() {
  if (!campaignsStore.currentCampaign || isCurrentCampaignOwned.value) {
    viewedPostIds.value = new Set();
    return;
  }

  try {
    const response = await apiService.get(`/campaigns/${campaignsStore.currentCampaign.id}/posts/viewed-status`);
    viewedPostIds.value = new Set(response.data.viewed_post_ids || []);
  } catch (error) {
    console.error('Failed to fetch viewed status:', error);
    viewedPostIds.value = new Set();
  }
}

async function markPostAsViewed(postId) {
  if (isCurrentCampaignOwned.value) return;

  const wasViewed = viewedPostIds.value.has(postId);

  // Optimistic update
  viewedPostIds.value.add(postId);

  try {
    await apiService.post(`/posts/${postId}/mark-viewed`);
  } catch (error) {
    console.error('Failed to mark post as viewed:', error);
    // Revert on error
    if (!wasViewed) {
      viewedPostIds.value.delete(postId);
    }
  }
}

// Watch for campaign changes to fetch viewed status
watch(() => campaignsStore.currentCampaign, () => {
  if (campaignsStore.currentCampaign) {
    fetchViewedStatus();
  }
});

// Watch for route changes to handle comment deep linking
watch(() => router.currentRoute.value.query.commentId, (newCommentId) => {
  if (newCommentId) {
    highlightedCommentId.value = parseInt(newCommentId);
    // Scroll to comment after a short delay to allow DOM to update
    setTimeout(() => {
      const commentElement = document.getElementById(`comment-${newCommentId}`);
      if (commentElement) {
        commentElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        // Clear highlight after animation
        setTimeout(() => {
          highlightedCommentId.value = null;
        }, 3000);
      }
    }, 500);
  }
}, { immediate: true });
</script>
