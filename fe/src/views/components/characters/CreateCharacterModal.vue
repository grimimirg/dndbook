<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click="handleClose">
      <div class="modal-content character-modal" @click.stop>
        <button class="modal-close btn-circle flex-center" @click="handleClose">×</button>
        <h3>{{ isEditing ? t('character.editCharacter') : t('character.createCharacter') }}</h3>
        <br>

        <form @submit.prevent="handleSubmit" class="character-form">
          <div class="form-group">
            <label>{{ t('character.name') }} *</label>
            <input
                v-model="formData.name"
                type="text"
                :placeholder="t('character.namePlaceholder')"
                required
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>{{ t('character.race') }} *</label>
              <input
                  v-model="formData.race"
                  type="text"
                  :placeholder="t('character.racePlaceholder')"
                  required
              />
            </div>

            <div class="form-group">
              <label>{{ t('character.class') }} *</label>
              <input
                  v-model="formData.character_class"
                  type="text"
                  :placeholder="t('character.classPlaceholder')"
                  required
              />
            </div>
          </div>

          <div class="form-group">
            <label>{{ t('character.description') }}</label>
            <textarea
                v-model="formData.description"
                :placeholder="t('character.descriptionPlaceholder')"
                rows="4"
            ></textarea>
          </div>

          <div class="form-group">
            <label>{{ t('character.image') }}</label>
            <div class="image-upload-area">
              <div v-if="imagePreview" class="image-preview">
                <img :src="imagePreview" :alt="t('character.imagePreview')"/>
                <button type="button" @click="removeImage" class="remove-image-btn">
                  {{ t('character.removeImage') }}
                </button>
              </div>
              <div v-else class="upload-placeholder">
                <input
                    type="file"
                    ref="fileInput"
                    @change="handleFileChange"
                    accept="image/*"
                    class="file-input"
                />
                <button type="button" @click="$refs.fileInput.click()" class="upload-btn">
                  {{ t('character.uploadImage') }}
                </button>
              </div>
            </div>
          </div>

          <div class="modal-actions">
            <button type="button" @click="handleClose" class="secondary">
              {{ t('common.cancel') }}
            </button>
            <button type="submit" class="primary" :disabled="saving">
              {{ saving ? t('common.loading') : t('common.confirm') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import {ref, watch, computed} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCharactersStore} from '../../../stores/characters.store.js';
import config from '../../../config/config.js';

const props = defineProps({
  show: Boolean,
  character: Object,
  campaignId: Number
});

const emit = defineEmits(['close', 'success']);

const {t} = useI18n();
const charactersStore = useCharactersStore();

const formData = ref({
  name: '',
  race: '',
  character_class: '',
  description: ''
});

const imageFile = ref(null);
const imagePreview = ref(null);
const fileInput = ref(null);
const saving = ref(false);
const removeExistingImage = ref(false);

const isEditing = computed(() => !!props.character);

watch(() => props.show, (newVal) => {
  if (newVal) {
    if (props.character) {
      formData.value = {
        name: props.character.name || '',
        race: props.character.race || '',
        character_class: props.character.character_class || '',
        description: props.character.description || ''
      };
      if (props.character.image_url) {
        const imageUrl = props.character.image_url.startsWith('http')
            ? props.character.image_url
            : `${config.API_BASE_URL}${props.character.image_url}`;
        imagePreview.value = imageUrl;
      }
    } else {
      resetForm();
    }
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});

function resetForm() {
  formData.value = {
    name: '',
    race: '',
    character_class: '',
    description: ''
  };
  imageFile.value = null;
  imagePreview.value = null;
  removeExistingImage.value = false;
}

function handleFileChange(event) {
  const file = event.target.files[0];
  if (file) {
    imageFile.value = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.value = e.target.result;
    };
    reader.readAsDataURL(file);
    removeExistingImage.value = false;
  }
}

function removeImage() {
  imageFile.value = null;
  imagePreview.value = null;
  removeExistingImage.value = true;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

async function handleSubmit() {
  saving.value = true;

  const submitData = new FormData();
  submitData.append('name', formData.value.name);
  submitData.append('race', formData.value.race);
  submitData.append('character_class', formData.value.character_class);
  submitData.append('description', formData.value.description || '');

  if (imageFile.value) {
    submitData.append('image', imageFile.value);
  } else if (removeExistingImage.value && isEditing.value) {
    submitData.append('remove_image', 'true');
  }

  let result;
  if (isEditing.value) {
    result = await charactersStore.updateCharacter(
        props.campaignId,
        props.character.id,
        submitData
    );
  } else {
    result = await charactersStore.createCharacter(props.campaignId, submitData);
  }

  saving.value = false;

  if (result.success) {
    emit('success');
    resetForm();
  } else {
    alert(result.error || t('common.error'));
  }
}

function handleClose() {
  resetForm();
  emit('close');
}
</script>

<style scoped>
.character-modal {
  max-width: 600px;
  width: 90%;
}

.character-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  font-weight: 500;
  font-size: 14px;
}

.form-group input,
.form-group textarea {
  padding: 0.5rem;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
}

.form-group textarea {
  resize: vertical;
}

.image-upload-area {
  border: 2px dashed var(--border-color);
  border-radius: 4px;
  padding: 1rem;
  text-align: center;
}

.image-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.image-preview img {
  max-width: 200px;
  max-height: 200px;
  border-radius: 4px;
  object-fit: cover;
}

.remove-image-btn {
  padding: 0.5rem 1rem;
  background-color: var(--danger-color, #dc3545);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.remove-image-btn:hover {
  opacity: 0.9;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.file-input {
  display: none;
}

.upload-btn {
  padding: 0.5rem 1rem;
  background-color: var(--primary-color);
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.upload-btn:hover {
  opacity: 0.9;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
</style>
