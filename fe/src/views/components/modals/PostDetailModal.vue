<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click="handleClose">
      <div class="modal-content" @click.stop>
        <span class="close-btn btn-circle btn-circle-md" @click="handleClose">×</span>

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

        <div v-if="!isEditing" class="modal-meta flex-align-center">
          <span>{{ t('post.by') }}: {{ post.author }}</span>
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
                class="modal-image"
            />

            <div v-if="post.images && post.images.length > 1" class="image-controls flex-align-center">
              <button @click="previousImage" class="nav-button" :disabled="currentImageIndex === 0">‹</button>
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
                class="hidden-file-input"
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

        <div v-if="isEditing" class="edit-actions flex-end" style="margin-top: 1rem;">
          <button class="cancel-button" @click="cancelEditing">
            {{ t('post.cancel') }}
          </button>
          <button class="save-button" @click="saveChanges" :disabled="saving">
            {{ saving ? t('common.loading') : t('post.save') }}
          </button>
        </div>

        <div v-if="!isEditing" class="modal-actions flex-end">
          <button v-if="!isEditing" class="edit-button" @click="startEditing">
            {{ t('post.edit') }}
          </button>
          <button class="delete-button-modal" @click="$emit('delete')">
            {{ t('post.delete') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import {ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {usePostsStore} from '../../../stores/posts.store.js';

const {t} = useI18n();
const postsStore = usePostsStore();

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  post: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['close', 'delete', 'mark-viewed']);

const currentImageIndex = ref(0);
const isEditing = ref(false);
const editedTitle = ref('');
const editedContent = ref('');
const saving = ref(false);
const fileInput = ref(null);

watch(() => props.show, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden';
    currentImageIndex.value = 0;
    isEditing.value = false;
    emit('mark-viewed', props.post.id);
  } else {
    document.body.style.overflow = '';
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
</script>

<style scoped>
.modal-image {
  max-width: 100%;
  max-height: 600px;
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.modal-content::-webkit-scrollbar {
  width: 8px;
}

.modal-content::-webkit-scrollbar-track {
  background: var(--input-bg);
  border-radius: 4px;
}

.modal-content::-webkit-scrollbar-thumb {
  background: rgba(139, 111, 71, 0.5);
  border-radius: 4px;
}

.modal-content::-webkit-scrollbar-thumb:hover {
  background: rgba(139, 111, 71, 0.7);
}
</style>
