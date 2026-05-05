<template>
  <div :id="`post-${post.id}`" class="post-card card">
    <div class="post-header">
      <h3 class="post-title" @click="openModal">{{ post.title }}</h3>
      <div class="post-header-actions flex-align-center">
        <span v-if="!isOwner && !isViewed" class="checkmark-icon" :title="t('post.unviewed')">✓</span>
        <button v-if="isOwner" class="delete-button" @click.stop="showDeletePostConfirm = true" :title="t('post.delete')">
          ×
        </button>
      </div>
      <div class="post-meta flex-align-center">
        <span>{{ t('post.by') }}: {{ post.author }}</span>
        <span>{{ t('post.created') }}: {{ formatDate(post.created_at) }}</span>
        <span v-if="post.updated_at !== post.created_at">
          {{ t('post.updated') }}: {{ formatDate(post.updated_at) }}
        </span>
        <span v-if="post.importance_level > 0" class="importance-indicator" :title="post.importance_level">
          {{ '!'.repeat(post.importance_level) }}
        </span>
      </div>
    </div>

    <div v-if="post.images && post.images.length > 0" class="post-images">
      <div class="image-grid" :class="`grid-${Math.min(post.images.length, 3)}`">
        <div
            v-for="(image, index) in post.images.slice(0, 3)"
            :key="index"
            class="grid-image"
            @click="openModalWithImage(index)"
        >
          <img :src="getImageUrl(image.file_path)" :alt="`Post image ${index + 1}`" />
          <div v-if="index === 2 && post.images.length > 3" class="more-images-overlay">
            <span>{{ t('post.moreImages', { count: post.images.length - 3 }) }}</span>
          </div>
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
            :id="`comment-${comment.id}`"
            :class="{ 'highlighted': highlightedCommentId === comment.id }"
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

              <div v-if="permissionsStore.isCommentOwner(comment)" class="comment-actions flex-align-center"
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
        :start-image-index="modalImageIndex"
        :is-owner="isOwner"
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
  </div>
</template>

<script setup>
import {computed, ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {usePostsStore} from '../../../stores/posts.store.js';
import {useAuthStore} from '../../../stores/auth.store.js';
import {usePermissionsStore} from '../../../stores/permissions.store.js';
import ConfirmModal from '../modals/ConfirmModal.vue';
import PostDetailModal from '../modals/PostDetailModal.vue';

const {t} = useI18n();
const postsStore = usePostsStore();
const authStore = useAuthStore();
const permissionsStore = usePermissionsStore();

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
  },
  highlightedCommentId: {
    type: Number,
    default: null
  }
});

const PREVIEW_CHAR_LIMIT = parseInt(import.meta.env.VITE_POST_PREVIEW_LIMIT || '200');

const showModal = ref(false);
const modalImageIndex = ref(0);
const newCommentContent = ref('');
const editingCommentId = ref(null);
const editedCommentContent = ref('');
const hoveredCommentId = ref(null);
const showComments = ref(false);
const showDeletePostConfirm = ref(false);
const showDeleteCommentConfirm = ref(false);
const commentToDelete = ref(null);

const currentUserId = computed(() => authStore.user?.id);
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
  modalImageIndex.value = 0;
  showModal.value = true;
}

function openModalWithImage(index) {
  modalImageIndex.value = index;
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

async function confirmDeletePost() {
  showDeletePostConfirm.value = false;
  const result = await postsStore.deletePost(props.post.id);

  if (result.success) {
    closeModal();
  } else {
    alert(result.error || t('common.error'));
  }
}

async function handleAddComment() {
  if (!newCommentContent.value.trim()) return;

  const result = await postsStore.createComment(
    props.post.id,
    newCommentContent.value,
    props.post.title,
    props.post.campaign_name
  );

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
.image-grid {
  display: grid;
  gap: 4px;
  margin-bottom: 1rem;
}

.grid-1 {
  grid-template-columns: 1fr;
}

.grid-2 {
  grid-template-columns: 1fr 1fr;
}

.grid-3 {
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
}

.grid-3 .grid-image:nth-child(3) {
  grid-column: span 2;
}

.grid-image {
  position: relative;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  border-radius: 4px;
  cursor: pointer;
}

.grid-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.more-images-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 1.5rem;
  font-weight: bold;
}
</style>
