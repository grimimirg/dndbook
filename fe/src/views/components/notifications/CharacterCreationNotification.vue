<template>
  <Teleport to="body">
    <div v-if="show" class="notification-overlay">
      <div class="character-creation-notification">
        <button @click="handleDismiss" class="dismiss-btn">×</button>
        
        <div class="notification-content">
          <div v-if="mode === 'free'" class="free-mode">
            <h4>{{ t('character.createYourCharacter') }}</h4>
            <p>{{ t('character.createYourCharacterDesc') }}</p>
          </div>
          
          <div v-else-if="mode === 'predefined'" class="predefined-mode">
            <h4>{{ t('character.chooseYourCharacter') }}</h4>
            <p>{{ t('character.chooseYourCharacterDesc') }}</p>
          </div>
          
          <div class="notification-actions">
            <button v-if="mode === 'free'" @click="handleCreate" class="primary">
              {{ t('character.createCharacter') }}
            </button>
            <button v-if="mode === 'predefined'" @click="handleChoose" class="primary">
              {{ t('character.chooseCharacter') }}
            </button>
            <button @click="handleDismiss" class="secondary">
              {{ t('common.later') }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  show: Boolean,
  mode: {
    type: String,
    validator: (value) => ['free', 'predefined'].includes(value)
  },
  campaignId: Number
});

const emit = defineEmits(['dismiss', 'create', 'choose']);

let autoDismissTimer = null;

onMounted(() => {
  // Auto-dismiss after 30 seconds
  autoDismissTimer = setTimeout(() => {
    handleDismiss();
  }, 30000);
});

onUnmounted(() => {
  if (autoDismissTimer) {
    clearTimeout(autoDismissTimer);
  }
});

function handleDismiss() {
  if (autoDismissTimer) {
    clearTimeout(autoDismissTimer);
  }
  emit('dismiss');
}

function handleCreate() {
  handleDismiss();
  emit('create');
}

function handleChoose() {
  handleDismiss();
  emit('choose');
}
</script>
