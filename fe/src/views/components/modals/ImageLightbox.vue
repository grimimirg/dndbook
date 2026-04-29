<template>
  <Teleport to="body">
    <div v-if="show" class="lightbox-overlay" @click="handleOverlayClick">
      <div class="lightbox-content" @click.stop>
        <img 
          :src="getImageUrl(images[currentIndex].file_path)" 
          alt="Lightbox image" 
          class="lightbox-image"
        />

        <div v-if="images.length > 1" class="lightbox-controls flex-align-center">
          <button @click="previousImage" class="lightbox-nav-button nav-button">‹</button>
          <span class="lightbox-counter image-counter">{{ currentIndex + 1 }} / {{ images.length }}</span>
          <button @click="nextImage" class="lightbox-nav-button nav-button">›</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  images: {
    type: Array,
    required: true
  },
  initialIndex: {
    type: Number,
    default: 0
  }
});

const emit = defineEmits(['close']);

const currentIndex = ref(props.initialIndex);

function getImageUrl(filePath) {
  if (!filePath) return '';
  if (filePath.startsWith('http')) return filePath;
  return filePath;
}

function nextImage() {
  if (currentIndex.value < props.images.length - 1) {
    currentIndex.value++;
  } else {
    currentIndex.value = 0;
  }
}

function previousImage() {
  if (currentIndex.value > 0) {
    currentIndex.value--;
  } else {
    currentIndex.value = props.images.length - 1;
  }
}

function handleOverlayClick() {
  emit('close');
}

function handleKeyDown(event) {
  if (event.key === 'Escape') {
    emit('close');
  }
}

watch(() => props.initialIndex, (newIndex) => {
  currentIndex.value = newIndex;
});

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});
</script>

<style scoped>
.lightbox-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10020;
  padding: 20px;
}

.lightbox-content {
  position: relative;
  max-width: 90vw;
  max-height: 90vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.lightbox-image {
  max-width: 90vw;
  max-height: 90vh;
  object-fit: contain;
  display: block;
}

.lightbox-controls {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  gap: 16px;
  background: var(--card-bg-1);
  padding: 8px 16px;
  border-radius: 20px;
  border: 1px solid rgba(139, 111, 71, 0.3);
}

.lightbox-nav-button {
  background: transparent;
  color: var(--text-heading);
  font-size: 24px;
  padding: 0 8px;
  border: none;
  text-transform: none;
  letter-spacing: normal;
}

.lightbox-nav-button:hover {
  background: rgba(139, 111, 71, 0.3);
  transform: none;
}
</style>
