<template>
  <div :id="`post-${post.id}`" class="post-card card">
    <div class="post-header">
      <h3 class="post-title" @click="openModal">{{ post.title }}</h3>
      <div class="post-header-actions flex-align-center">
        <span v-if="!isOwner && !isViewed" class="checkmark-icon" :title="t('post.unviewed')">✓</span>
        <button class="delete-button" @click.stop="showDeletePostConfirm = true" :title="t('post.delete')">
          ×
        </button>
      </div>
      <div class="post-meta flex-align-center">
        <span>{{ t('post.by') }}: {{ post.author }}</span>
        <span>{{ t('post.created') }}: {{ formatDate(post.created_at) }}</span>
        <span v-if="post.updated_at !== post.created_at">
          {{ t('post.updated') }}: {{ formatDate(post.updated_at) }}
        </span>
      </div>
    </div>

    <div v-if="post.images && post.images.length > 0" class="post-images">
      <div class="image-container">
        <img :src="getImageUrl(post.images[currentImageIndex].file_path)" alt="Post image" class="post-image" @click="openLightbox(currentImageIndex)"/>

        <div v-if="post.images.length > 1" class="image-controls flex-align-center">
          <button @click="previousImage" class="nav-button" :disabled="currentImageIndex === 0">‹</button>
          <span class="image-counter">{{ currentImageIndex + 1 }} / {{ post.images.length }}</span>
          <button @click="nextImage" class="nav-button">›</button>
        </div>
      </div>
    </div>

    <div class="post-content">
      {{ truncatedContent }}
      <span v-if="isContentTruncated" class="read-more" @click="openModal">
        {{ t('post.readMore') }}
      </span>
    </div>

    <div class="comments-section">
      <div class="comments-header flex-between" @click="toggleComments">
        <h4>{{ t('comment.comments') }} ({{ post.comments?.length || 0 }})</h4>
      </div>

      <div v-show="showComments" v-if="post.comments && post.comments.length > 0" class="comments-list">
        <div
            v-for="comment in post.comments"
            :key="comment.id"
            class="comment-item flex-between"
            @mouseenter="hoveredCommentId = comment.id"
            @mouseleave="hoveredCommentId = null"
        >
          <div class="comment-content">
            <div class="comment-header flex-between">
              <div class="comment-info flex-align-baseline">
                <span class="comment-author">{{ comment.author }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              </div>

              <div v-if="comment.author_id === currentUserId" class="comment-actions flex-align-center"
                   :class="{ 'visible': hoveredCommentId === comment.id }">
                <button
                    v-if="editingCommentId !== comment.id"
                    @click="startEditComment(comment)"
                    class="comment-action-btn edit-btn"
                    :title="t('comment.edit')"
                >
                  ✎
                </button>
                <button
                    v-if="editingCommentId !== comment.id"
                    @click="handleDeleteComment(comment.id)"
                    class="comment-action-btn edit-btn"
                    :title="t('comment.delete')"
                >
                  ✕
                </button>
                <button
                    v-if="editingCommentId === comment.id"
                    @click="saveEditComment(comment.id)"
                    class="comment-action-btn save-btn"
                    :title="t('comment.save')"
                >
                  ✓
                </button>
                <button
                    v-if="editingCommentId === comment.id"
                    @click="cancelEditComment"
                    class="comment-action-btn edit-btn"
                    :title="t('comment.cancel')"
                >
                  ✕
                </button>
              </div>

            </div>
            <p v-if="editingCommentId !== comment.id" class="comment-text">{{ comment.content }}</p>
            <textarea
                v-else
                v-model="editedCommentContent"
                class="comment-edit-input"
                @keydown.esc="cancelEditComment"
            />
          </div>

        </div>
      </div>

      <div v-show="showComments" class="comment-input-container flex-align-center">
        <textarea
            v-model="newCommentContent"
            :placeholder="t('comment.writeComment')"
            class="comment-input"
        />
        <span
            @click="handleAddComment"
            class="comment-post-btn"
            :class="{ 'disabled': !newCommentContent.trim() }"
            :title="t('comment.post')"
        >
          🪶
        </span>
      </div>
    </div>

    <PostDetailModal
        :show="showModal"
        :post="post"
        @close="closeModal"
        @delete="showDeletePostConfirm = true"
        @mark-viewed="emitMarkViewed"
    />

    <ConfirmModal
        :show="showDeletePostConfirm"
        :title="t('post.deleteTitle')"
        :message="t('post.confirmDelete')"
        @confirm="confirmDeletePost"
        @cancel="showDeletePostConfirm = false"
    />

    <ConfirmModal
        :show="showDeleteCommentConfirm"
        :title="t('comment.deleteTitle')"
        :message="t('comment.confirmDelete')"
        @confirm="confirmDeleteComment"
        @cancel="cancelDeleteComment"
    />

    <ImageLightbox
        :show="showLightbox"
        :images="post.images"
        :initial-index="lightboxImageIndex"
        @close="closeLightbox"
    />
  </div>
</template>

<script setup>
import {computed, ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {usePostsStore} from '../../stores/posts.store.js';
import {useAuthStore} from '../../stores/auth.store.js';
import ConfirmModal from './modals/ConfirmModal.vue';
import PostDetailModal from './modals/PostDetailModal.vue';
import ImageLightbox from './modals/ImageLightbox.vue';

const {t} = useI18n();
const postsStore = usePostsStore();
const authStore = useAuthStore();

const emit = defineEmits(['mark-viewed']);

const props = defineProps({
  post: {
    type: Object,
    required: true
  },
  isViewed: {
    type: Boolean,
    default: false
  },
  isOwner: {
    type: Boolean,
    default: false
  }
});

const PREVIEW_CHAR_LIMIT = parseInt(import.meta.env.VITE_POST_PREVIEW_LIMIT || '200');

const currentImageIndex = ref(0);
const showModal = ref(false);
const showLightbox = ref(false);
const lightboxImageIndex = ref(0);
const newCommentContent = ref('');
const editingCommentId = ref(null);
const editedCommentContent = ref('');
const hoveredCommentId = ref(null);
const showComments = ref(false);
const showDeletePostConfirm = ref(false);
const showDeleteCommentConfirm = ref(false);
const commentToDelete = ref(null);

const truncatedContent = computed(() => {
  if (props.post.content.length <= PREVIEW_CHAR_LIMIT) {
    return props.post.content;
  }
  return props.post.content.substring(0, PREVIEW_CHAR_LIMIT) + '...';
});

const isContentTruncated = computed(() => {
  return props.post.content.length > PREVIEW_CHAR_LIMIT;
});

function openModal() {
  showModal.value = true;
}

function closeModal() {
  showModal.value = false;
}

function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
}

function getImageUrl(filePath) {
  if (!filePath) return '';
  if (filePath.startsWith('http')) return filePath;
  return filePath;
}

function previousImage() {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--;
  } else {
    currentImageIndex.value = props.post.images.length - 1;
  }
}

function nextImage() {
  if (currentImageIndex.value < props.post.images.length - 1) {
    currentImageIndex.value++;
  } else {
    currentImageIndex.value = 0;
  }
}

function openLightbox(index) {
  lightboxImageIndex.value = index;
  showLightbox.value = true;
}

function closeLightbox() {
  showLightbox.value = false;
}

async function confirmDeletePost() {
  showDeletePostConfirm.value = false;
  const result = await postsStore.deletePost(props.post.id);

  if (result.success) {
    closeModal();
  } else {
    alert(result.error || t('common.error'));
  }
}

const currentUserId = computed(() => authStore.user?.id);

async function handleAddComment() {
  if (!newCommentContent.value.trim()) return;

  const result = await postsStore.createComment(props.post.id, newCommentContent.value);

  if (result.success) {
    newCommentContent.value = '';
  } else {
    alert(result.error || t('common.error'));
  }
}

function startEditComment(comment) {
  editingCommentId.value = comment.id;
  editedCommentContent.value = comment.content;
}

function cancelEditComment() {
  editingCommentId.value = null;
  editedCommentContent.value = '';
}

async function saveEditComment(commentId) {
  if (!editedCommentContent.value.trim()) {
    alert(t('common.error'));
    return;
  }

  const result = await postsStore.updateComment(props.post.id, commentId, editedCommentContent.value);

  if (result.success) {
    editingCommentId.value = null;
    editedCommentContent.value = '';
  } else {
    alert(result.error || t('common.error'));
  }
}

function handleDeleteComment(commentId) {
  commentToDelete.value = commentId;
  showDeleteCommentConfirm.value = true;
}

async function confirmDeleteComment() {
  showDeleteCommentConfirm.value = false;
  const result = await postsStore.deleteComment(props.post.id, commentToDelete.value);

  if (!result.success) {
    alert(result.error || t('common.error'));
  }
  commentToDelete.value = null;
}

function cancelDeleteComment() {
  showDeleteCommentConfirm.value = false;
  commentToDelete.value = null;
}

function toggleComments() {
  showComments.value = !showComments.value;
}

function emitMarkViewed(postId) {
  emit('mark-viewed', postId);
}
</script>

<style scoped>
.post-header-actions {
  gap: 8px;
}

.checkmark-icon {
  color: var(--success-color, #4caf50);
  font-weight: bold;
  font-size: 1.2em;
  cursor: default;
}

.post-image {
  width: 100%;
  height: 300px;
  object-fit: cover;
  object-position: top;
  display: block;
  cursor: pointer;
}
</style>
