<template>
  <div v-if="show" class="modal" @click.self="handleClose">
    <div class="modal-content">
      <div class="modal-header flex-between">
        <h3>{{ t('campaign.importTitle') }}</h3>
        <button @click="handleClose" class="close-btn btn-circle btn-circle-md">×</button>
      </div>
      
      <div class="modal-body">
        <p class="instruction">{{ t('campaign.importDescription') }}</p>
        
        <div class="file-upload-area">
          <input 
            ref="fileInput"
            type="file" 
            accept=".zip"
            @change="handleFileSelect"
            class="file-input"
            id="campaign-import-file"
          />
          <label for="campaign-import-file" class="file-label">
            <span class="file-icon">📦</span>
            <span v-if="selectedFile" class="file-name">{{ selectedFile.name }}</span>
            <span v-else class="file-placeholder">{{ t('campaign.selectFile') }}</span>
          </label>
        </div>
        
        <div v-if="error" class="error">{{ error }}</div>
      </div>
      
      <div class="modal-footer flex-end">
        <button @click="handleClose" class="secondary">{{ t('campaign.cancel') }}</button>
        <button 
          @click="handleImport" 
          class="primary" 
          :disabled="!selectedFile || importing"
        >
          {{ importing ? t('common.loading') : t('campaign.uploadAndImport') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import axios from 'axios';

const props = defineProps({
  show: Boolean
});

const emit = defineEmits(['close', 'success']);

const { t } = useI18n();

const selectedFile = ref(null);
const importing = ref(false);
const error = ref('');
const fileInput = ref(null);

function handleFileSelect(event) {
  const file = event.target.files[0];
  if (file) {
    if (!file.name.endsWith('.zip')) {
      error.value = 'Only ZIP files are supported';
      selectedFile.value = null;
      return;
    }
    selectedFile.value = file;
    error.value = '';
  }
}

async function handleImport() {
  if (!selectedFile.value) return;
  
  importing.value = true;
  error.value = '';
  
  try {
    const formData = new FormData();
    formData.append('archive', selectedFile.value);
    
    const token = localStorage.getItem('token');
    const response = await axios.post(
      `${import.meta.env.VITE_API_URL}/api/import`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        }
      }
    );
    
    if (response.data) {
      emit('success', response.data);
      handleClose();
    }
  } catch (err) {
    console.error('Import error:', err);
    error.value = err.response?.data?.error || t('campaign.importError');
  } finally {
    importing.value = false;
  }
}

function handleClose() {
  selectedFile.value = null;
  error.value = '';
  if (fileInput.value) {
    fileInput.value.value = '';
  }
  emit('close');
}
</script>
