<template>
  <div :id="`post-${post.id}`" class="post-card card">
    <div class="post-header">
      <h3>{{ post.title }}</h3>
      <div class="post-meta">
        <span>Created: {{ formatDate(post.created_at) }}</span>
        <span v-if="post.updated_at !== post.created_at">
          Updated: {{ formatDate(post.updated_at) }}
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
      {{ post.content }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  post: {
    type: Object,
    required: true
  }
})

const currentImageIndex = ref(0)

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
</style>
