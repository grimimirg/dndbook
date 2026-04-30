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
