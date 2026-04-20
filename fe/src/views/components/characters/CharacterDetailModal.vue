<template>
  <Teleport to="body">
    <div v-if="show && character" class="modal-overlay" @click="handleClose">
      <div class="modal-content character-detail-modal" @click.stop>
        <button class="close-btn btn-circle btn-circle-md" @click="handleClose">×</button>

        <div class="character-detail-content">
          <div class="character-header">
            <div v-if="character.image_url" class="character-image">
              <img :src="getImageUrl(character.image_url)" :alt="character.name"/>
            </div>
            <div class="character-title">
              <h2>{{ character.name }}</h2>
              <div class="character-subtitle">
                <span class="race">{{ character.race }}</span>
                <span class="separator">•</span>
                <span class="class">{{ character.character_class }}</span>
              </div>
              <br>
              <div v-if="character.description" class="character-description">
                <p>{{ character.description }}</p>
              </div>
              <div v-else class="no-description">
                {{ t('character.noDescription') }}
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script setup>
import {watch} from 'vue';
import {useI18n} from 'vue-i18n';
import config from '../../../config/config.js';

const props = defineProps({
  show: Boolean,
  character: Object
});

const emit = defineEmits(['close']);

const {t} = useI18n();

function getImageUrl(imageUrl) {
  if (!imageUrl) return '';
  if (imageUrl.startsWith('http')) return imageUrl;
  return `${config.API_BASE_URL}${imageUrl}`;
}

function handleClose() {
  emit('close');
}

watch(() => props.show, (newVal) => {
  if (newVal) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});
</script>

<style scoped>
.character-detail-modal {
  max-width: 600px;
  width: 90%;
}

.character-detail-content {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.character-header {
  display: flex;
  gap: 1.5rem;
  align-items: flex-start;
}

.character-image {
  flex-shrink: 0;
  width: 200px;
  height: 300px;
  border-radius: 8px;
  overflow: hidden;
  border: 3px solid var(--border-color);
}

.character-image img {
  width: 100%;
  height: 100%;
  object-fit: contain;
  background-color: var(--secondary-bg);
}

.character-title {
  flex: 1;
}

.character-title h2 {
  margin: 0 0 0.5rem 0;
  font-size: 24px;
  color: var(--text-primary);
}

.character-subtitle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 16px;
  color: var(--text-secondary);
}

.separator {
  color: var(--text-tertiary);
}

.character-description h4 {
  margin: 0 0 0.75rem 0;
  font-size: 16px;
  color: var(--text-primary);
}

.character-description p {
  margin: 0;
  line-height: 1.6;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-wrap: break-word;
  word-break: break-all;
}

.no-description {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
  font-style: italic;
}

</style>
