<template>
  <Teleport to="body">
    <div v-if="show" class="confirm-modal-overlay" @click="handleCancel">
      <div class="confirm-modal-content" @click.stop>
        <h3 class="confirm-modal-title">{{ title }}</h3>
        <p class="confirm-modal-message">{{ message }}</p>
        
        <div class="confirm-modal-actions">
          <button 
            @click="handleCancel" 
            class="confirm-modal-btn cancel-btn"
            :title="t('common.cancel')"
          >
            ✕
          </button>
          <button 
            @click="handleConfirm" 
            class="confirm-modal-btn confirm-btn"
            :title="t('common.confirm')"
          >
            ✓
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    required: true
  },
  message: {
    type: String,
    required: true
  }
});

const emit = defineEmits(['confirm', 'cancel']);

function handleConfirm() {
  emit('confirm');
}

function handleCancel() {
  emit('cancel');
}
</script>
