<template>
  <div class="notification-container">
    <transition name="notification">
      <div v-if="show" :class="['notification', type]" class="flex-align-center">
        <div class="notification-icon">{{ icon }}</div>
        <div class="notification-content">
          <div class="notification-message">{{ message }}</div>
        </div>
        <button @click="close" class="notification-close btn-circle btn-circle-sm">×</button>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue';

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  },
  type: {
    type: String,
    default: 'success',
    validator: (value) => ['success', 'error'].includes(value)
  },
  message: {
    type: String,
    required: true
  },
  duration: {
    type: Number,
    default: 3000
  }
});

const emit = defineEmits(['close']);

const icon = computed(() => {
  return props.type === 'success' ? '✓' : '✕';
});

let timeoutId = null;

watch(() => props.show, (newValue) => {
  if (newValue && props.duration > 0) {
    timeoutId = setTimeout(() => {
      close();
    }, props.duration);
  } else if (!newValue && timeoutId) {
    clearTimeout(timeoutId);
  }
});

function close() {
  emit('close');
}
</script>

