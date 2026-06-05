<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="show"
        class="resources-backdrop"
        @click="$emit('close')"
      />
    </Transition>
    <Transition name="slide-panel">
      <div
        v-if="show"
        class="resources-panel"
        role="dialog"
        aria-modal="true"
        :aria-label="t('campaign.resourcesTitle')"
      >
        <div class="resources-panel-header flex-between">
          <h3>{{ t('campaign.resourcesTitle') }}</h3>
          <button class="menu-toggle-btn" @click="$emit('close')" :title="t('common.close')">✕</button>
        </div>
        <div class="resources-panel-body">
          <p class="resources-empty">{{ t('campaign.resourcesEmpty') }}</p>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { onUnmounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

const props = defineProps({
  show: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close']);

function onKeydown(e) {
  if (e.key === 'Escape') emit('close');
}

watch(() => props.show, (val) => {
  if (val) {
    document.addEventListener('keydown', onKeydown);
  } else {
    document.removeEventListener('keydown', onKeydown);
  }
});

onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown);
});
</script>

<style scoped>
.resources-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 900;
}

.resources-panel {
  position: fixed;
  left: 0;
  top: 0;
  width: 300px;
  height: 100vh;
  background: linear-gradient(145deg, var(--card-bg-1) 0%, var(--card-bg-2) 100%);
  border-right: 1px solid rgba(139, 111, 71, 0.3);
  box-shadow: 4px 0 16px rgba(0, 0, 0, 0.3);
  z-index: 901;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.resources-panel-header {
  padding: 16px;
  border-bottom: 1px solid rgba(139, 111, 71, 0.2);
  flex-shrink: 0;
}

.resources-panel-header h3 {
  font-size: 16px;
}

.resources-panel-body {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.resources-empty {
  color: var(--text-secondary);
  font-style: italic;
  font-size: 14px;
}

/* transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-panel-enter-active,
.slide-panel-leave-active {
  transition: transform 0.3s ease;
}
.slide-panel-enter-from,
.slide-panel-leave-to {
  transform: translateX(-100%);
}
</style>
