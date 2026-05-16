<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click="handleClose">
      <div class="modal-content post-detail-modal" @click.stop>
        <span class="close-btn btn-circle btn-circle-md" @click="handleClose">×</span>

        <div class="modal-title-row" v-if="!isEditing">
          <h2>{{ post.title }}</h2>
          <span v-if="post.importance_level > 0" class="importance-indicator" :title="post.importance_level">
              {{ '👑'.repeat(post.importance_level) }}
          </span>
        </div>
        <textarea
            v-else
            v-model="editedTitle"
            class="edit-title"
            :placeholder="t('post.title')"
        />

        <div v-if="!isEditing" class="modal-meta flex-align-center">
          <span>{{ t('post.by') }}: {{ post.author }}</span>
          <span>{{ t('post.created') }}: {{ formatDate(post.created_at) }}</span>
          <span v-if="post.updated_at !== post.created_at">
            {{ t('post.updated') }}: {{ formatDate(post.updated_at) }}
          </span>
        </div>

        <div v-if="(post.images && post.images.length > 0) || isEditing" class="modal-images">
          <div class="image-gallery">
            <div class="image-container">
              <button v-if="post.images && post.images.length > 1" @click="previousImage" class="nav-button nav-left"
                      :disabled="currentImageIndex === 0">‹
              </button>
              <img
                  v-if="post.images && post.images.length > 0"
                  :src="getImageUrl(post.images[currentImageIndex].file_path)"
                  alt="Post image"
                  class="modal-image"
              />
              <button v-if="post.images && post.images.length > 1" @click="nextImage" class="nav-button nav-right">›
              </button>
            </div>

            <div class="image-description-panel">
              <p
                  v-if="!isEditing && post.images && post.images.length > 0"
                  class="image-description-text-view"
              >
                {{ post.images[currentImageIndex].description || '' }}
              </p>
              <textarea
                  v-if="isEditing && post.images && post.images.length > 0"
                  v-model="editedImageDescriptions[currentImageIndex]"
                  :placeholder="t('post.imageDescription')"
                  class="image-description-text"
              ></textarea>
            </div>
          </div>

          <div v-if="isEditing" class="image-edit-controls">
            <input
                type="file"
                ref="fileInput"
                @change="handleImageUpload"
                accept="image/*"
                multiple
                class="hidden-file-input"
            />
            <div class="flex gap-2 pt-2">

              <button class="upload-button" @click="$refs.fileInput.click()">
                {{ t('post.uploadImage') }}
              </button>
              <button
                  v-if="post.images && post.images.length > 0"
                  class="remove-image-button"
                  @click="removeCurrentImage"
              >
                {{ t('post.removeImage') }}
              </button>
            </div>
          </div>

        </div>

        <div class="modal-body">
          <div v-if="!isEditing" v-html="renderedContent" @click="handleContentClick"></div>
          <div v-else>
            <textarea
                ref="editContentTextarea"
                v-model="editedContent"
                class="edit-content"
                :placeholder="t('post.content')"
                @input="handleEditContentInput"
                @keydown="handleEditKeydown"
                @click="handleEditClick"
            />
            <MentionAutocomplete
                :show="showMentionAutocomplete"
                :query="mentionQuery"
                :campaign-id="post.campaign_id"
                :textarea-ref="editContentTextarea"
                @select="handleMentionSelect"
                @close="closeMentionAutocomplete"
                ref="mentionAutocomplete"
            />
          </div>
        </div>

        <div v-if="isEditing" class="edit-importance">
          <label>{{ t('post.importance') }}</label>
          <div class="importance-selector">
            <span
                v-for="i in 10"
                :key="i"
                @click="editedImportanceLevel = i"
                class="importance-mark"
                :class="{ active: i <= editedImportanceLevel }"
            >
              👑
            </span>
          </div>
        </div>

        <div v-if="isEditing && isOwner" class="edit-visibility">
          <div class="visibility-toggle flex-align-center" @click="editedIsHidden = !editedIsHidden" style="cursor: pointer;">
            <input type="checkbox" v-model="editedIsHidden" class="hidden-checkbox" @click.stop />
            <span class="eye-toggle" :title="t('post.hideFromPlayers')">
              {{ editedIsHidden ? '🔒' : '👁️' }}
            </span>
            <span>{{ t('post.hideFromPlayers') }}</span>
          </div>
        </div>

        <div v-if="isEditing" class="edit-actions flex-end" style="margin-top: 1rem;">
          <button class="cancel-button" @click="cancelEditing">
            {{ t('post.cancel') }}
          </button>
          <button class="save-button" @click="saveChanges" :disabled="saving">
            {{ saving ? t('common.loading') : t('post.save') }}
          </button>
        </div>

        <div v-if="!isEditing" class="modal-actions flex-end">
          <button v-if="!isEditing && permissionsStore.canEditPost(props.post)" class="edit-button"
                  @click="startEditing">
            {{ t('post.edit') }}
          </button>
          <button v-if="isOwner" class="delete-button-modal" @click="$emit('delete')">
            {{ t('post.delete') }}
          </button>
        </div>

        <div v-if="!isEditing" class="comments-section">
          <div class="comments-header flex-between">
            <h4>{{ t('comment.comments') }} ({{ post.comments?.length || 0 }})</h4>
          </div>

          <div v-if="post.comments && post.comments.length > 0" class="comments-list">
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

          <div class="comment-input-container flex-align-center">
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
      </div>
    </div>

    <ConfirmModal
        :show="showDeleteCommentConfirm"
        :title="t('comment.deleteTitle')"
        :message="t('comment.confirmDelete')"
        @confirm="confirmDeleteComment"
        @cancel="cancelDeleteComment"
    />

    <CharacterDetailModal
        :show="showCharacterDetail"
        :character="selectedCharacter"
        @close="showCharacterDetail = false"
    />
  </Teleport>
</template>

<script setup>
import {onMounted, onUnmounted, ref, watch, computed} from 'vue';
import {useI18n} from 'vue-i18n';
import {usePostsStore} from '../../../stores/posts.store.js';
import {usePermissionsStore} from '../../../stores/permissions.store.js';
import {useCampaignsStore} from '../../../stores/campaigns.store.js';
import {useMentionRenderer} from '../../../composables/useMentionRenderer.js';
import ConfirmModal from './ConfirmModal.vue';
import CharacterDetailModal from '../left/characters/CharacterDetailModal.vue';
import MentionAutocomplete from '../MentionAutocomplete.vue';

const {t} = useI18n();
const {renderContentWithMentions} = useMentionRenderer();
const postsStore = usePostsStore();
const permissionsStore = usePermissionsStore();
const campaignsStore = useCampaignsStore();

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  post: {
    type: Object,
    required: true
  },
  startInEditMode: {
    type: Boolean,
    default: false
  },
  isOwner: {
    type: Boolean,
    default: false
  },
  startImageIndex: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['close', 'delete', 'mark-viewed']);

const currentImageIndex = ref(0);
const isEditing = ref(false);
const editedTitle = ref('');
const editedContent = ref('');
const editedImportanceLevel = ref(0);
const editedIsHidden = ref(false);
const editedImageDescriptions = ref({});
const saving = ref(false);
const fileInput = ref(null);
const newCommentContent = ref('');
const editingCommentId = ref(null);
const editedCommentContent = ref('');
const hoveredCommentId = ref(null);
const showDeleteCommentConfirm = ref(false);
const commentToDelete = ref(null);
const highlightedCommentId = ref(null);
const showCharacterDetail = ref(false);
const selectedCharacter = ref(null);
const editContentTextarea = ref(null);
const mentionAutocomplete = ref(null);

// Mention autocomplete state
const showMentionAutocomplete = ref(false);
const mentionQuery = ref('');
const mentionStartIndex = ref(0);

let touchStartX = 0;
let touchEndX = 0;

const renderedContent = computed(() => {
  return renderContentWithMentions(props.post.content, props.post.character_mentions || []);
});

onMounted(() => {
  document.addEventListener('keydown', handleKeydown);
  document.addEventListener('touchstart', handleTouchStart);
  document.addEventListener('touchend', handleTouchEnd);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeydown);
  document.removeEventListener('touchstart', handleTouchStart);
  document.removeEventListener('touchend', handleTouchEnd);
});

watch(() => props.show, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden';
    currentImageIndex.value = props.startImageIndex || 0;
    if (props.post.images) {
      editedImageDescriptions.value = props.post.images.reduce((acc, img, idx) => {
        acc[idx] = img.description || '';
        return acc;
      }, {});
    }
    if (props.startInEditMode && permissionsStore.canEditPost(props.post)) {
      isEditing.value = true;
      editedTitle.value = props.post.title;
      editedContent.value = props.post.content;
      editedImportanceLevel.value = props.post.importance_level || 0;
      editedIsHidden.value = props.post.is_hidden || false;
    } else {
      isEditing.value = false;
    }
    emit('mark-viewed', props.post.id);
  } else {
    document.body.style.overflow = '';
  }
});

watch(() => currentImageIndex.value, (newIndex) => {
  if (props.post && props.post.images && props.post.images[newIndex]) {
    if (editedImageDescriptions.value[newIndex] === undefined) {
      editedImageDescriptions.value[newIndex] = props.post.images[newIndex].description || '';
    }
  }
});

function handleClose() {
  emit('close');
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

function startEditing() {
  if (!permissionsStore.canEditPost(props.post)) {
    return;
  }
  isEditing.value = true;
  editedTitle.value = props.post.title;
  editedContent.value = props.post.content;
  editedImportanceLevel.value = props.post.importance_level || 0;
  editedIsHidden.value = props.post.is_hidden || false;
}

function cancelEditing() {
  isEditing.value = false;
  editedTitle.value = '';
  editedContent.value = '';
  editedImportanceLevel.value = 0;
  editedIsHidden.value = false;
}

function handleKeydown(event) {
  if (!props.show || !props.post.images || props.post.images.length <= 1) return;

  if (event.key === 'ArrowLeft') {
    previousImage();
  } else if (event.key === 'ArrowRight') {
    nextImage();
  }
}

function handleTouchStart(event) {
  touchStartX = event.changedTouches[0].screenX;
}

function handleTouchEnd(event) {
  touchEndX = event.changedTouches[0].screenX;
  handleSwipe();
}

function handleSwipe() {
  if (!props.show || !props.post.images || props.post.images.length <= 1) return;

  const swipeThreshold = 50;
  const diff = touchStartX - touchEndX;

  if (Math.abs(diff) > swipeThreshold) {
    if (diff > 0) {
      nextImage();
    } else {
      previousImage();
    }
  }
}

async function saveChanges() {
  if (!editedTitle.value.trim() || !editedContent.value.trim()) {
    alert(t('common.error'));
    return;
  }

  saving.value = true;

  const descriptionsToSave = {...editedImageDescriptions.value};

  if (props.post.images) {
    for (const [index, image] of props.post.images.entries()) {
      const description = descriptionsToSave[index] ?? '';
      await postsStore.updateImageDescription(
          props.post.id,
          image.id,
          description,
          index
      );
    }
  }

  const result = await postsStore.updatePost(props.post.id, {
    title: editedTitle.value,
    content: editedContent.value,
    importance_level: editedImportanceLevel.value,
    is_hidden: editedIsHidden.value
  });

  if (result.success) {
    isEditing.value = false;
  } else {
    alert(result.error || t('common.error'));
  }

  saving.value = false;
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
  const files = Array.from(event.target.files);
  if (files.length === 0) return;

  if (props.post.images && props.post.images.length + files.length > 10) {
    alert(t('post.maxImagesWarning', {max: 10}));
    return;
  }

  for (const file of files) {
    const result = await postsStore.uploadImage(props.post.id, file, '', props.post.images ? props.post.images.length : 0);

    if (result.success) {
      if (!props.post.images) {
        props.post.images = [];
      }
      props.post.images.push(result.image);
      currentImageIndex.value = props.post.images.length - 1;
    } else {
      alert(result.error || t('common.error'));
    }
  }

  event.target.value = '';
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

function handleContentClick(event) {
  const target = event.target;
  if (target.classList.contains('character-mention')) {
    const characterId = parseInt(target.dataset.characterId);
    const mention = props.post.character_mentions?.find(m => m.character_id === characterId);
    if (mention && mention.character) {
      selectedCharacter.value = mention.character;
      showCharacterDetail.value = true;
    }
  }
}

function handleEditContentInput(event) {
  const textarea = event.target;
  const cursorPosition = textarea.selectionStart;
  const textBeforeCursor = editedContent.value.substring(0, cursorPosition);

  // Check if we just typed @
  const lastChar = textBeforeCursor.slice(-1);
  if (lastChar === '@') {
    showMentionAutocomplete.value = true;
    mentionQuery.value = '';
    mentionStartIndex.value = cursorPosition - 1;
  } else if (showMentionAutocomplete.value) {
    // Extract the word after @
    const atIndex = textBeforeCursor.lastIndexOf('@');
    if (atIndex !== -1) {
      const wordAfterAt = textBeforeCursor.substring(atIndex + 1);
      // Check if there's a space after @
      if (wordAfterAt.includes(' ')) {
        closeMentionAutocomplete();
      } else {
        mentionQuery.value = wordAfterAt;
      }
    } else {
      closeMentionAutocomplete();
    }
  }
}

function handleEditKeydown(event) {
  if (showMentionAutocomplete.value && mentionAutocomplete.value) {
    mentionAutocomplete.value.handleKeydown(event);
  }
}

function handleEditClick() {
  closeMentionAutocomplete();
}

function handleMentionSelect(character) {
  if (!editContentTextarea.value) return;

  const textarea = editContentTextarea.value;
  const cursorPosition = textarea.selectionStart;
  const textBeforeMention = editedContent.value.substring(0, mentionStartIndex.value);
  const textAfterCursor = editedContent.value.substring(cursorPosition);

  // Replace @query with @character_name
  editedContent.value = textBeforeMention + `@${character.name}` + textAfterCursor;

  // Set cursor position after the mention
  const newCursorPosition = mentionStartIndex.value + character.name.length + 1;
  textarea.setSelectionRange(newCursorPosition, newCursorPosition);
  textarea.focus();

  closeMentionAutocomplete();
}

function closeMentionAutocomplete() {
  showMentionAutocomplete.value = false;
  mentionQuery.value = '';
}
</script>
