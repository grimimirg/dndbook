<template>
  <div class="post-creator card">
    <form @submit.prevent="handleCreatePost">
      <div class="form-group">
        <input v-model="title" :placeholder="t('post.title')" required />
      </div>
      <div class="form-group">
        <textarea
          v-model="content"
          :placeholder="t('post.content')"
          rows="4"
          required
        ></textarea>
      </div>

      <div class="form-group">
        <label>{{ t('post.importance') }}</label>
        <div class="importance-selector">
          <span
              v-for="i in 10"
              :key="i"
              @click="importanceLevel = i"
              class="importance-mark"
              :class="{ active: i <= importanceLevel }"
          >
            !
          </span>
        </div>
      </div>

      <div v-if="selectedImages.length > 0" class="image-previews">
        <div v-for="(image, index) in selectedImages" :key="index" class="image-preview">
          <img :src="image.preview" :alt="`Preview ${index + 1}`" />
          <button @click="moveImageUp(index)" v-if="index > 0" class="move-image btn-circle btn-circle-sm">↑</button>
          <button @click="moveImageDown(index)" v-if="index < selectedImages.length - 1" class="move-image btn-circle btn-circle-sm">↓</button>
          <button @click="removeImage(index)" class="remove-image btn-circle btn-circle-sm">×</button>
          <textarea
            v-model="image.description"
            :placeholder="t('post.imageDescription')"
            class="image-description"
            rows="2"
          ></textarea>
        </div>
      </div>

      <div v-if="selectedImages.length >= 10" class="max-images-warning">
        {{ t('post.maxImagesWarning', { max: 10 }) }}
      </div>
      
      <div class="actions flex-between">
        <label class="image-upload-btn flex-align-center">
          <input 
            type="file" 
            ref="fileInput"
            @change="handleImageSelect" 
            accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
            multiple
            class="hidden-file-input"
          />
          <span class="upload-icon">📷</span>
          <span>{{ t('post.addImages') }}</span>
        </label>
        <button type="submit" class="primary" :disabled="loading">
          {{ loading ? t('post.creating') : t('post.createPost') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCampaignsStore } from '../../../stores/campaigns.store.js';
import { usePostsStore } from '../../../stores/posts.store.js';

const { t } = useI18n();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();

const title = ref('');
const content = ref('');
const importanceLevel = ref(0);
const loading = ref(false);
const selectedImages = ref([]);
const fileInput = ref(null);

function handleImageSelect(event) {
  const files = Array.from(event.target.files);

  if (selectedImages.value.length + files.length > 10) {
    alert(t('post.maxImagesWarning', { max: 10 }));
    return;
  }

  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        selectedImages.value.push({
          file: file,
          preview: e.target.result,
          description: ''
        });
      };
      reader.readAsDataURL(file);
    }
  });

  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

function removeImage(index) {
  selectedImages.value.splice(index, 1);
}

function moveImageUp(index) {
  if (index > 0) {
    const temp = selectedImages.value[index];
    selectedImages.value[index] = selectedImages.value[index - 1];
    selectedImages.value[index - 1] = temp;
  }
}

function moveImageDown(index) {
  if (index < selectedImages.value.length - 1) {
    const temp = selectedImages.value[index];
    selectedImages.value[index] = selectedImages.value[index + 1];
    selectedImages.value[index + 1] = temp;
  }
}

async function handleCreatePost() {
  if (!campaignsStore.currentCampaign) return;
  
  loading.value = true;
  
  const result = await postsStore.createPost(
    campaignsStore.currentCampaign.id,
    title.value,
    content.value,
    importanceLevel.value
  );
  
  if (result.success && result.post) {
    const postId = result.post.id;

    for (const [index, image] of selectedImages.value.entries()) {
      await postsStore.uploadImage(postId, image.file, image.description, index);
    }

    await postsStore.fetchPosts(campaignsStore.currentCampaign.id);

    title.value = '';
    content.value = '';
    importanceLevel.value = 0;
    selectedImages.value = [];
  }
  
  loading.value = false;
}
</script>

<style scoped>
.importance-selector {
  display: flex;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.importance-mark {
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-color);
  opacity: 0.3;
  transition: opacity 0.2s, color 0.2s;
  user-select: none;
}

.importance-mark:hover {
  opacity: 0.6;
}

.importance-mark.active {
  color: #e74c3c;
  opacity: 1;
}
</style>
