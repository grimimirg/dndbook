<template>
  <div :id="`post-${post.id}`" class="post-card card">
    <div class="post-header">
      <h3 class="post-title" @click="openModal">{{ post.title }}</h3>
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
        <img :src="getImageUrl(post.images[currentImageIndex].file_path)" alt="Post image" />
        
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

    <Teleport to="body">
      <div v-if="showModal" class="modal-overlay" @click="closeModal">
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="closeModal">×</button>
          <h2>{{ post.title }}</h2>
          <div class="modal-meta">
            <span v-if="post.author">{{ t('post.author') }}: {{ post.author }}</span>
            <span>{{ t('post.created') }}: {{ formatDate(post.created_at) }}</span>
            <span v-if="post.updated_at !== post.created_at">
              {{ t('post.updated') }}: {{ formatDate(post.updated_at) }}
            </span>
          </div>
          <div v-if="post.images && post.images.length > 0" class="modal-images">
            <div class="image-container">
              <img :src="getImageUrl(post.images[currentImageIndex].file_path)" alt="Post image" />
              
              <div v-if="post.images.length > 1" class="image-controls">
                <button @click="previousImage" class="nav-button">‹</button>
                <span class="image-counter">{{ currentImageIndex + 1 }} / {{ post.images.length }}</span>
                <button @click="nextImage" class="nav-button">›</button>
              </div>
            </div>
          </div>
          <div class="modal-body">
            {{ post.content }}
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const PREVIEW_CHAR_LIMIT = parseInt(import.meta.env.VITE_POST_PREVIEW_LIMIT || '200')

const currentImageIndex = ref(0)
const showModal = ref(false)

const truncatedContent = computed(() => {
  if (props.post.content.length <= PREVIEW_CHAR_LIMIT) {
    return props.post.content
  }
  return props.post.content.substring(0, PREVIEW_CHAR_LIMIT) + '...'
})

const isContentTruncated = computed(() => {
  return props.post.content.length > PREVIEW_CHAR_LIMIT
})

function openModal() {
  showModal.value = true
  document.body.style.overflow = 'hidden'
}

function closeModal() {
  showModal.value = false
  document.body.style.overflow = ''
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('en-US', { 
    year: 'numeric', 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getImageUrl(filePath) {
  return `http://localhost:5000/uploads/${filePath}`
}

function previousImage() {
  if (currentImageIndex.value > 0) {
    currentImageIndex.value--
  } else {
    currentImageIndex.value = props.post.images.length - 1
  }
}

function nextImage() {
  if (currentImageIndex.value < props.post.images.length - 1) {
    currentImageIndex.value++
  } else {
    currentImageIndex.value = 0
  }
}
</script>

<style scoped>
.post-card {
  scroll-margin-top: 80px;
}

.post-header h3 {
  margin-bottom: 8px;
  font-size: 20px;
}

.post-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #65676b;
  margin-bottom: 12px;
}

.post-images {
  margin-bottom: 12px;
}

.image-container {
  position: relative;
  background: #f0f2f5;
  border-radius: 8px;
  overflow: hidden;
}

.image-container img {
  width: 100%;
  display: block;
}

.image-controls {
  position: absolute;
  bottom: 16px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 16px;
  background: rgba(0, 0, 0, 0.6);
  padding: 8px 16px;
  border-radius: 20px;
}

.nav-button {
  background: transparent;
  color: white;
  font-size: 24px;
  padding: 0 8px;
}

.nav-button:hover {
  background: rgba(255, 255, 255, 0.1);
}

.image-counter {
  color: white;
  font-size: 14px;
}

.post-content {
  white-space: pre-wrap;
  line-height: 1.5;
}

.post-title {
  cursor: pointer;
  transition: color 0.2s;
}

.post-title:hover {
  color: #1877f2;
}

.read-more {
  color: #1877f2;
  cursor: pointer;
  font-weight: 600;
  margin-left: 4px;
}

.read-more:hover {
  text-decoration: underline;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 8px;
  max-width: 800px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.modal-close {
  position: absolute;
  top: 16px;
  right: 16px;
  background: #f0f2f5;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
  color: #65676b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s;
}

.modal-close:hover {
  background: #e4e6eb;
}

.modal-content h2 {
  margin: 0 40px 16px 0;
  font-size: 24px;
  color: #050505;
}

.modal-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #65676b;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.modal-images {
  margin-bottom: 16px;
}

.modal-body {
  white-space: pre-wrap;
  line-height: 1.6;
  color: #050505;
  font-size: 15px;
}
</style>
