<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click="handleClose">
      <div class="modal-content" @click.stop>
        <span class="close-btn btn-circle btn-circle-md" @click="handleClose">×</span>

        <h2 v-if="!isEditing">{{ post.title }}</h2>
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
          <p v-if="!isEditing">{{ post.content }}</p>
          <textarea
              v-else
              v-model="editedContent"
              class="edit-content"
              :placeholder="t('post.content')"
          />
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
              !
            </span>
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
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import {onMounted, onUnmounted, ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {usePostsStore} from '../../../stores/posts.store.js';
import {usePermissionsStore} from '../../../stores/permissions.store.js';

const {t} = useI18n();
const postsStore = usePostsStore();
const permissionsStore = usePermissionsStore();

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
const editedImageDescriptions = ref({});
const saving = ref(false);
const fileInput = ref(null);

let touchStartX = 0;
let touchEndX = 0;

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
}

function cancelEditing() {
  isEditing.value = false;
  editedTitle.value = '';
  editedContent.value = '';
  editedImportanceLevel.value = 0;
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
    importance_level: editedImportanceLevel.value
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

</script>
