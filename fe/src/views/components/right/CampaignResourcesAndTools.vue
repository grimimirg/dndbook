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
