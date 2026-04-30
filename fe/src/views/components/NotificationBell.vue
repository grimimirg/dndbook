<template>
  <div class="notification-bell">
    <button @click="toggleDropdown" class="bell-button" :class="{ 'has-notifications': unreadCount > 0 }"
            :title="t('notification.title')">
      <span class="bell-icon">🔔</span>
      <span v-if="unreadCount > 0" class="badge">{{ unreadCount }}</span>
    </button>

    <div v-if="showDropdown" class="dropdown" @click.stop>
      <div class="dropdown-header flex-between">
        <h3>{{ t('notification.title') }}</h3>
        <button @click="showDropdown = false" class="close-btn btn-circle btn-circle-md">×</button>
      </div>

      <div v-if="loading" class="loading">
        {{ t('common.loading') }}
      </div>

      <div v-else-if="notifications.length === 0" class="empty-state">
        {{ t('notification.empty') }}
      </div>

      <div v-else class="notifications-list">
        <div
            v-for="notification in notifications"
            :key="notification.id"
            class="notification-item"
            @click="handleNotificationClick(notification)"
        >
          <div class="notification-content">
            <div class="notification-type">{{ getNotificationTypeLabel(notification.notification_type) }}</div>
            <div class="notification-message">{{ notification.message }}</div>
            <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
          </div>
          <!-- Invite-specific actions -->
          <div v-if="notification.notification_type === 'invite'" class="invite-actions flex-align-center">
            <button @click.stop="handleAccept(notification)" class="accept-btn">
              {{ t('invite.accept') }}
            </button>
            <button @click.stop="handleReject(notification)" class="reject-btn">
              {{ t('invite.reject') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import {onMounted, onUnmounted, ref, watch} from 'vue';
import {useRouter} from 'vue-router';
import {useI18n} from 'vue-i18n';
import {useInvitesStore} from '../../stores/invites.store.js';
import {useCampaignsStore} from '../../stores/campaigns.store.js';
import apiService from '../../services/api.service.js';
import socketService from '../../services/socket.service.js';

const router = useRouter();
const {t} = useI18n();
const invitesStore = useInvitesStore();
const campaignsStore = useCampaignsStore();

const showDropdown = ref(false);
const loading = ref(false);
const notifications = ref([]);
const unreadCount = ref(0);

function toggleDropdown() {
  showDropdown.value = !showDropdown.value;
}

function getNotificationTypeLabel(type) {
  return t(`notification.type.${type}`);
}

async function fetchNotifications() {
  loading.value = true;
  try {
    const response = await apiService.get('/notifications');
    notifications.value = response.data.notifications;
  } catch (error) {
    console.error('Failed to fetch notifications:', error);
  } finally {
    loading.value = false;
  }
}

async function fetchUnreadCount() {
  try {
    const response = await apiService.get('/notifications/unread');
    unreadCount.value = response.data.count;
  } catch (error) {
    console.error('Failed to fetch unread count:', error);
  }
}

async function deleteNotifications() {
  try {
    await apiService.delete('/notifications');
    notifications.value = [];
    unreadCount.value = 0;
  } catch (error) {
    console.error('Failed to delete notifications:', error);
  }
}

async function handleAccept(notification) {
  // For invite notifications, we need to find the corresponding invite
  // and use the existing invites store logic
  const inviteId = notification.related_invite_id; // This would need to be stored in notification
  if (inviteId) {
    const result = await invitesStore.acceptInvite(inviteId);
    if (result.success) {
      campaignsStore.addSharedCampaign(result.campaign);
      // Remove notification from list
      notifications.value = notifications.value.filter(n => n.id !== notification.id);
    }
  }
}

async function handleReject(notification) {
  const inviteId = notification.related_invite_id;
  if (inviteId) {
    await invitesStore.rejectInvite(inviteId);
    // Remove notification from list
    notifications.value = notifications.value.filter(n => n.id !== notification.id);
  }
}

function handleNotificationClick(notification) {
  showDropdown.value = false;

  if (notification.related_post_id) {
    // Navigate to the post with optional comment anchor
    const route = { name: 'home' };
    if (notification.related_comment_id) {
      route.query = { commentId: notification.related_comment_id };
    }
    router.push(route);
  }
}

function formatTime(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMs / 3600000);
  const diffDays = Math.floor(diffMs / 86400000);

  if (diffMins < 1) return t('notification.justNow');
  if (diffMins < 60) return t('notification.minutesAgo', {n: diffMins});
  if (diffHours < 24) return t('notification.hoursAgo', {n: diffHours});
  if (diffDays < 7) return t('notification.daysAgo', {n: diffDays});
  return date.toLocaleDateString();
}

function handleClickOutside(event) {
  const dropdown = document.querySelector('.notification-bell');
  if (dropdown && !dropdown.contains(event.target)) {
    showDropdown.value = false;
  }
}

function handleNotificationUpdate() {
  // WebSocket event handler - refresh unread count
  fetchUnreadCount();
}

// Watch for dropdown open to fetch notifications
watch(showDropdown, async (newVal) => {
  if (newVal) {
    await fetchNotifications();
  } else {
    // Delete notifications when popup closes
    await deleteNotifications();
  }
});

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
  fetchUnreadCount();

  // Set up WebSocket listener for notification updates
  socketService.on('notification_update', handleNotificationUpdate);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
  socketService.off('notification_update');
});
</script>
