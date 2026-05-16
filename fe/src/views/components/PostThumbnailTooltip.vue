<template>
  <Teleport to="body">
    <div v-if="show" class="post-thumbnail-tooltip" :style="tooltipStyle">
      <div v-if="hasImages" class="thumbnail-grid">
        <img
          v-for="(image, index) in displayImages"
          :key="index"
          :src="loadedImages[index] || placeholderImage"
          :alt="`Thumbnail ${index + 1}`"
          class="thumbnail-image"
          :class="{ 'loading': !loadedImages[index] }"
          @load="onImageLoad(index, $event)"
          @error="onImageError(index)"
          loading="lazy"
        />
      </div>
      <div v-else class="no-images-placeholder">
        <span>{{ t('post.noImages') }}</span>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  post: {
    type: Object,
    required: true
  },
  position: {
    type: Object,
    default: () => ({ x: 0, y: 0 })
  }
});

const placeholderImage = '/images/placeholder.svg';
const loadedImages = ref({});
const tooltipStyle = ref({});

const hasImages = computed(() => {
  return props.post.images && props.post.images.length > 0;
});

const displayImages = computed(() => {
  if (!hasImages.value) return [];
  return props.post.images.slice(0, 3);
});

function getImageUrl(filePath) {
  if (!filePath) return '';
  if (filePath.startsWith('http')) return filePath;
  return filePath;
}

function onImageLoad(index, event) {
  loadedImages.value[index] = event.target.src;
}

function onImageError(index) {
  loadedImages.value[index] = placeholderImage;
}

function updateTooltipPosition() {
  if (!props.show) return;
  
  const tooltip = document.querySelector('.post-thumbnail-tooltip');
  if (!tooltip) return;

  const tooltipRect = tooltip.getBoundingClientRect();
  const viewportWidth = window.innerWidth;
  const viewportHeight = window.innerHeight;

  let left = props.position.x + 10;
  let top = props.position.y;

  if (left + tooltipRect.width > viewportWidth - 10) {
    left = props.position.x - tooltipRect.width - 10;
  }

  if (top + tooltipRect.height > viewportHeight - 10) {
    top = props.position.y - tooltipRect.height;
  }

  tooltipStyle.value = {
    left: `${left}px`,
    top: `${top}px`
  };
}

watch(() => props.show, (newValue) => {
  if (newValue) {
    loadedImages.value = {};
    displayImages.value.forEach((image, index) => {
      const img = new Image();
      img.src = getImageUrl(image.file_path);
      img.onload = (e) => onImageLoad(index, e);
      img.onerror = () => onImageError(index);
    });
    setTimeout(updateTooltipPosition, 0);
  }
});

watch(() => props.position, () => {
  updateTooltipPosition();
});
</script>
