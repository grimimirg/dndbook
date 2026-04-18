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
      
      <div v-if="selectedImages.length > 0" class="image-previews">
        <div v-for="(image, index) in selectedImages" :key="index" class="image-preview">
          <img :src="image.preview" :alt="`Preview ${index + 1}`" />
          <button type="button" class="remove-image" @click="removeImage(index)" :title="t('post.removeImage')">
            ×
          </button>
        </div>
      </div>
      
      <div class="actions">
        <label class="image-upload-btn">
          <input 
            type="file" 
            ref="fileInput"
            @change="handleImageSelect" 
            accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
            multiple
            style="display: none;"
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
import { useCampaignsStore } from '../../stores/campaigns.store.js';
import { usePostsStore } from '../../stores/posts.store.js';

const { t } = useI18n();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();

const title = ref('');
const content = ref('');
const loading = ref(false);
const selectedImages = ref([]);
const fileInput = ref(null);

function handleImageSelect(event) {
  const files = Array.from(event.target.files);
  
  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        selectedImages.value.push({
          file: file,
          preview: e.target.result
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

async function handleCreatePost() {
  if (!campaignsStore.currentCampaign) return;
  
  loading.value = true;
  
  const result = await postsStore.createPost(
    campaignsStore.currentCampaign.id,
    title.value,
    content.value
  );
  
  if (result.success && result.post) {
    const postId = result.post.id;
    
    for (const image of selectedImages.value) {
      await postsStore.uploadImage(postId, image.file);
    }
    
    await postsStore.fetchPosts(campaignsStore.currentCampaign.id);
    
    title.value = '';
    content.value = '';
    selectedImages.value = [];
  }
  
  loading.value = false;
}
</script>
