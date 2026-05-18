<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <h3>{{ t('campaign.create') }}</h3><br>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <input v-model="localName" :placeholder="t('campaign.name')" required/>
        </div>
        <div class="form-group">
          <textarea v-model="localDescription" :placeholder="t('campaign.description')" rows="4"></textarea>
          <button type="button" class="generate-setup-btn" @click="generateSetup">
            🎲 {{ t('campaign.generateSetup') }}
          </button>
        </div>
        <div class="form-group mode-group">
          <div class="mode-select-wrapper">
            <label>{{ t('campaign.characterCreationMode') }}</label>
            <select v-model="localCharacterCreationMode" class="form-select">
              <option value="optional">{{ t('campaign.modeOptional') }}</option>
              <option value="free">{{ t('campaign.modeFree') }}</option>
              <option value="predefined">{{ t('campaign.modePredefined') }}</option>
            </select>
          </div>
          <p class="mode-description">{{ getModeDescription(localCharacterCreationMode) }}</p>
        </div>
        <div class="modal-actions" style="display: flex; justify-content: flex-end; gap: 1rem;">
          <button type="button" @click="$emit('close')" class="secondary">{{ t('campaign.cancel') }}</button>
          <button type="submit" class="primary">{{ t('campaign.createButton') }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import {ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {generateCampaign} from '../../../utils/campaignGenerator.js';

const {t} = useI18n();

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  }
});

const emit = defineEmits(['close', 'create']);

const localName = ref('');
const localDescription = ref('');
const localCharacterCreationMode = ref('optional');

watch(() => props.show, (newValue) => {
  if (!newValue) {
    localName.value = '';
    localDescription.value = '';
    localCharacterCreationMode.value = 'optional';
  }
});

function getModeDescription(mode) {
  switch (mode) {
    case 'optional':
      return t('campaign.modeOptionalDesc');
    case 'free':
      return t('campaign.modeFreeDesc');
    case 'predefined':
      return t('campaign.modePredefinedDesc');
    default:
      return '';
  }
}

function generateSetup() {
  localDescription.value = generateCampaign();
}

function handleSubmit() {
  emit('create', {
    name: localName.value,
    description: localDescription.value,
    characterCreationMode: localCharacterCreationMode.value
  });
}
</script>
