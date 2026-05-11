<template>
  <div class="post-item flex-align-center" :class="{ 'hidden-post-item': post.is_hidden && isOwner }">
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
