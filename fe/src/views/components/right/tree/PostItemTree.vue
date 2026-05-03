<template>
  <div class="post-item flex-align-center">
    <span v-if="!isOwner && !viewedPostIds.has(post.id)" class="checkmark-icon">✓</span>
    <span class="post-title" @click="scrollToPost(post.id)">{{ post.title }}</span>
    <button
        v-if="permissionsStore.isPostOwner(post)"
        @click.stop="togglePostMenu(post.id, $event)"
        class="menu-toggle-btn"
    >
      ⋮
    </button>
  </div>
</template>

<script setup>
import {usePermissionsStore} from '../../../../stores/permissions.store.js';

const props = defineProps({
  post: {
    type: Object,
    required: true
  },
  isOwner: {
    type: Boolean,
    default: false
  },
  viewedPostIds: {
    type: Set,
    default: () => new Set()
  }
});

const emit = defineEmits(['scroll-to-post', 'toggle-post-menu']);

const permissionsStore = usePermissionsStore();

function scrollToPost(postId) {
  emit('scroll-to-post', postId);
}

function togglePostMenu(postId, event) {
  emit('toggle-post-menu', postId, event);
}
</script>

<style scoped>
.post-item {
  padding: 12px 8px;
  gap: 8px;
  line-height: 1.3;
  min-height: 32px;
  margin: 0;
  display: flex;
  align-items: center;
}

.post-item span,
.post-item button {
  margin: 0;
  padding: 0;
  line-height: 1.3;
}

.post-item .menu-toggle-btn {
  opacity: 0;
  margin-left: auto;
}

.post-item:hover .menu-toggle-btn {
  opacity: 1;
}
</style>
