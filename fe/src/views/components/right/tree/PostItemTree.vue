<template>
  <div 
    class="post-item flex-align-center" 
    :class="{ 'hidden-post-item': post.is_hidden && isOwner }"
    @mouseenter="handleMouseEnter"
    @mouseleave="handleMouseLeave"
  >
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
  <PostThumbnailTooltip
    :show="showTooltip"
    :post="post"
    :position="tooltipPosition"
  />
</template>

<script setup>
import {ref} from 'vue';
import {usePermissionsStore} from '../../../../stores/permissions.store.js';
import PostThumbnailTooltip from '../../PostThumbnailTooltip.vue';

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
const showTooltip = ref(false);
const tooltipPosition = ref({ x: 0, y: 0 });
let hoverTimeout = null;

function handleMouseEnter(event) {
  if (hoverTimeout) {
    clearTimeout(hoverTimeout);
  }
  
  hoverTimeout = setTimeout(() => {
    showTooltip.value = true;
    updateTooltipPosition(event);
  }, 500);
}

function handleMouseLeave() {
  if (hoverTimeout) {
    clearTimeout(hoverTimeout);
    hoverTimeout = null;
  }
  showTooltip.value = false;
}

function updateTooltipPosition(event) {
  const rect = event.target.getBoundingClientRect();
  tooltipPosition.value = {
    x: rect.right,
    y: rect.top
  };
}

function scrollToPost(postId) {
  emit('scroll-to-post', postId);
}

function togglePostMenu(postId, event) {
  emit('toggle-post-menu', postId, event);
}
</script>
