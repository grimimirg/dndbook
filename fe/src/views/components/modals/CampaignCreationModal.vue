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

watch(() => props.show, (newValue) => {
  if (!newValue) {
    localName.value = '';
    localDescription.value = '';
  }
});

function handleSubmit() {
  emit('create', {
    name: localName.value,
    description: localDescription.value
  });
}
</script>
