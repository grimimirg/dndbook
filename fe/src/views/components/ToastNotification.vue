<template>
  <div class="toast-container">
    <transition name="toast">
      <div v-if="show" :class="['toast', type]" class="flex-align-center">
        <div class="toast-icon">{{ icon }}</div>
        <div class="toast-content">
          <div class="toast-message">{{ message }}</div>
        </div>
        <button @click="close" class="toast-close btn-circle btn-circle-sm">×</button>
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

<style scoped>
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 10040;
}

.toast {
  background: var(--card-bg-1);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  padding: 16px;
  min-width: 300px;
  max-width: 400px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  gap: 12px;
}

.toast.success {
  border-color: var(--success-color);
}

.toast.error {
  border-color: var(--danger);
}

.toast-icon {
  font-size: 24px;
  font-weight: bold;
  flex-shrink: 0;
}

.toast.success .toast-icon {
  color: var(--success-color);
}

.toast.error .toast-icon {
  color: var(--danger);
}

.toast-content {
  flex: 1;
}

.toast-message {
  font-size: 14px;
  color: var(--text-primary);
}

.toast-close {
  background: transparent;
  border: none;
  font-size: 24px;
  line-height: 1;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.toast-close:hover {
  color: var(--text-primary);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
