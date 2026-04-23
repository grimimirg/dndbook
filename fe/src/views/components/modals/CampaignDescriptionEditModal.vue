<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click="$emit('close')">
      <div class="modal-content" @click.stop>
        <h3>{{ t('campaign.editChronicle') }}</h3>
        <br>
        <div class="modal-body">
          <div class="form-group">
            <textarea
                v-model="localDescription"
                class="edit-description-textarea"
                :placeholder="t('campaign.description')"
                rows="10"
            />
          </div>
        </div>

        <div class="edit-actions flex-end">
          <button class="cancel-button" @click="$emit('close')">
            {{ t('post.cancel') }}
          </button>
          <button class="save-button" @click="$emit('save', localDescription)" :disabled="saving">
            {{ saving ? t('common.loading') : t('post.save') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import {ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';

const {t} = useI18n();

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  description: {
    type: String,
    default: ''
  },
  saving: {
    type: Boolean,
    default: false
  }
});

const emit = defineEmits(['close', 'save']);

const localDescription = ref(props.description);

watch(() => props.description, (newValue) => {
  localDescription.value = newValue;
});

watch(() => props.show, (newValue) => {
  if (newValue) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});
</script>
