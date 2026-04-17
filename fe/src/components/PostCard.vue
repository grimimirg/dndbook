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
