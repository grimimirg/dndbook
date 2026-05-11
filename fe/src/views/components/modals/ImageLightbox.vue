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

watch(() => props.initialIndex, (newIndex) => {
  currentIndex.value = newIndex;
});

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown);
});

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown);
});

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
</script>
