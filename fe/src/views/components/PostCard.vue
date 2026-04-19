<template>
  <div :id="`post-${post.id}`" class="post-card card">
    <div class="post-header">
      <h3 class="post-title" @click="openModal">{{ post.title }}</h3>
      <button class="delete-button" @click.stop="handleDelete" :title="t('post.delete')">
        ×
      </button>
      <div class="post-meta">
        <span v-if="post.author">{{ t('post.author') }}: {{ post.author }}</span>
        <span>{{ t('post.created') }}: {{ formatDate(post.created_at) }}</span>
        <span v-if="post.updated_at !== post.created_at">
          {{ t('post.updated') }}: {{ formatDate(post.updated_at) }}
        </span>
      </div>
    </div>

    <div v-if="post.images && post.images.length > 0" class="post-images">
      <div class="image-container">
        <img :src="getImageUrl(post.images[currentImageIndex].file_path)" alt="Post image"/>

        <div v-if="post.images.length > 1" class="image-controls">
          <button @click="previousImage" class="nav-button">‹</button>
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
      <div class="comments-header">
        <h4>{{ t('comment.comments') }} ({{ post.comments?.length || 0 }})</h4>
      </div>

      <div v-if="post.comments && post.comments.length > 0" class="comments-list">
        <div
            v-for="comment in post.comments"
            :key="comment.id"
            class="comment-item"
            @mouseenter="hoveredCommentId = comment.id"
            @mouseleave="hoveredCommentId = null"
        >
          <div class="comment-content">
            <div class="comment-header">
              <div class="comment-info">
                <span class="comment-author">{{ comment.author }}</span>
                <span class="comment-date">{{ formatDate(comment.created_at) }}</span>
              </div>

              <div v-if="comment.author_id === currentUserId" class="comment-actions" :class="{ 'visible': hoveredCommentId === comment.id }">
                <button
                    v-if="editingCommentId !== comment.id"
                    @click="startEditComment(comment)"
                    class="comment-action-btn edit-btn"
                    :title="t('comment.edit')"
                >
                  ✎
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
                    class="comment-action-btn cancel-btn"
                    :title="t('comment.cancel')"
                >
                  ✕
                </button>
                <button
                    v-if="editingCommentId !== comment.id"
                    @click="handleDeleteComment(comment.id)"
                    class="comment-action-btn delete-btn"
                    :title="t('comment.delete')"
                >
                  🗑
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

      <div class="comment-input-container">
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

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="closeModal">×</button>
          <div class="modal-actions">
            <button v-if="!isEditing" class="edit-button" @click="startEditing">
              {{ t('post.edit') }}
            </button>
            <button class="delete-button-modal" @click="handleDelete">
              {{ t('post.delete') }}
            </button>
          </div>

          <div v-if="isEditing" class="edit-mode-indicator">
            {{ t('post.editMode') }}
          </div>

          <h2 v-if="!isEditing">{{ post.title }}</h2>
          <textarea
              v-else
              v-model="editedTitle"
              class="edit-title"
              :placeholder="t('post.title')"
          />

          <div class="modal-meta">
            <span v-if="post.author">{{ t('post.author') }}: {{ post.author }}</span>
            <span>{{ t('post.created') }}: {{ formatDate(post.created_at) }}</span>
            <span v-if="post.updated_at !== post.created_at">
              {{ t('post.updated') }}: {{ formatDate(post.updated_at) }}
            </span>
          </div>

          <div v-if="(post.images && post.images.length > 0) || isEditing" class="modal-images">
            <div class="image-container">
              <img
                  v-if="post.images && post.images.length > 0"
                  :src="getImageUrl(post.images[currentImageIndex].file_path)"
                  alt="Post image"
              />

              <div v-if="post.images && post.images.length > 1" class="image-controls">
                <button @click="previousImage" class="nav-button">‹</button>
                <span class="image-counter">{{ currentImageIndex + 1 }} / {{ post.images.length }}</span>
                <button @click="nextImage" class="nav-button">›</button>
              </div>

              <button
                  v-if="isEditing && post.images && post.images.length > 0"
                  class="remove-image-button"
                  @click="removeCurrentImage"
              >
                {{ t('post.removeImage') }}
              </button>
            </div>

            <div v-if="isEditing" class="image-upload">
              <input
                  type="file"
                  ref="fileInput"
                  @change="handleImageUpload"
                  accept="image/*"
                  style="display: none"
              />
              <button class="upload-button" @click="$refs.fileInput.click()">
                {{ t('post.uploadImage') }}
              </button>
            </div>
          </div>

          <div class="modal-body">
            <p v-if="!isEditing">{{ post.content }}</p>
            <textarea
                v-else
                v-model="editedContent"
                class="edit-content"
                :placeholder="t('post.content')"
            />
          </div>

          <div v-if="isEditing" class="edit-actions">
            <button class="save-button" @click="saveChanges" :disabled="saving">
              {{ saving ? t('common.loading') : t('post.save') }}
            </button>
            <button class="cancel-button" @click="cancelEditing">
              {{ t('post.cancel') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import {computed, ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {usePostsStore} from '../../stores/posts.store.js';
import {useAuthStore} from '../../stores/auth.store.js';

const {t} = useI18n();
const postsStore = usePostsStore();
const authStore = useAuthStore();

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
});

const PREVIEW_CHAR_LIMIT = parseInt(import.meta.env.VITE_POST_PREVIEW_LIMIT || '200');

const currentImageIndex = ref(0);
const showModal = ref(false);
const isEditing = ref(false);
const editedTitle = ref('');
const editedContent = ref('');
const saving = ref(false);
const fileInput = ref(null);
const newCommentContent = ref('');
const editingCommentId = ref(null);
const editedCommentContent = ref('');
const hoveredCommentId = ref(null);

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
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  showModal.value = false;
  document.body.style.overflow = '';
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
  return `http://localhost:5000/uploads/${filePath}`;
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

function startEditing() {
  isEditing.value = true;
  editedTitle.value = props.post.title;
  editedContent.value = props.post.content;
}

function cancelEditing() {
  isEditing.value = false;
  editedTitle.value = '';
  editedContent.value = '';
}

async function saveChanges() {
  if (!editedTitle.value.trim() || !editedContent.value.trim()) {
    alert(t('common.error'));
    return;
  }

  saving.value = true;
  const result = await postsStore.updatePost(props.post.id, {
    title: editedTitle.value,
    content: editedContent.value
  });

  saving.value = false;

  if (result.success) {
    isEditing.value = false;
  } else {
    alert(result.error || t('common.error'));
  }
}

async function handleDelete() {
  if (!confirm(t('post.confirmDelete'))) {
    return;
  }

  const result = await postsStore.deletePost(props.post.id);

  if (result.success) {
    closeModal();
  } else {
    alert(result.error || t('common.error'));
  }
}

async function removeCurrentImage() {
  if (!props.post.images || props.post.images.length === 0) return;

  const imageToRemove = props.post.images[currentImageIndex.value];
  const result = await postsStore.deleteImage(props.post.id, imageToRemove.id);

  if (result.success) {
    props.post.images.splice(currentImageIndex.value, 1);
    if (currentImageIndex.value >= props.post.images.length && currentImageIndex.value > 0) {
      currentImageIndex.value--;
    }
  } else {
    alert(result.error || t('common.error'));
  }
}

async function handleImageUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const result = await postsStore.uploadImage(props.post.id, file);

  if (result.success) {
    if (!props.post.images) {
      props.post.images = [];
    }
    props.post.images.push(result.image);
    currentImageIndex.value = props.post.images.length - 1;
  } else {
    alert(result.error || t('common.error'));
  }

  event.target.value = '';
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

async function handleDeleteComment(commentId) {
  if (!confirm(t('comment.confirmDelete'))) {
    return;
  }

  const result = await postsStore.deleteComment(props.post.id, commentId);

  if (!result.success) {
    alert(result.error || t('common.error'));
  }
}
</script>
