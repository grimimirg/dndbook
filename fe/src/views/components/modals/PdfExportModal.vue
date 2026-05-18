<template>
  <div v-if="show" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content pdf-export-modal">
      <h2>{{ t('pdfExport.exportToPdf') }}</h2>
      
      <div class="style-options">
        <button
            v-for="style in styles"
            :key="style.value"
            @click="exportPdf(style.value)"
            class="style-option"
            :class="{ 'is-selected': selectedStyle === style.value }"
        >
          <span class="style-icon">{{ style.icon }}</span>
          <span class="style-name">{{ style.label }}</span>
        </button>
      </div>
      
      <button @click="$emit('close')" class="cancel-button">
        {{ t('common.cancel') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import apiService from '../../../services/api.service.js';
import { PdfStyleTypes, PdfStyleOptions } from '../../../constants/pdfStyleConstants.js';

const props = defineProps({
  show: {
    type: Boolean,
    required: true
  },
  campaignId: {
    type: Number,
    required: true
  }
});

const emit = defineEmits(['close']);

const { t } = useI18n();
const selectedStyle = ref(PdfStyleTypes.CLASSIC);
const isLoading = ref(false);

const styles = PdfStyleOptions.map(style => ({
  ...style,
  label: t(`pdfExport.style${style.label.charAt(0).toUpperCase() + style.label.slice(1)}`)
}));

async function exportPdf(style) {
  if (!props.campaignId) return;
  
  selectedStyle.value = style;
  isLoading.value = true;
  
  try {
    const response = await apiService.get(`/pdf-export/${props.campaignId}?style=${style}`, {
      responseType: 'blob'
    });
    
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    
    const contentDisposition = response.headers['content-disposition'];
    let filename = `campaign_${props.campaignId}_${style}.pdf`;
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '');
      }
    }
    
    link.setAttribute('download', filename);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);
    
    emit('close');
  } catch (error) {
    console.error('PDF export failed:', error);
    alert(t('pdfExport.exportFailed'));
  } finally {
    isLoading.value = false;
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.modal-content {
  background: var(--card-bg-2);
  border-radius: 12px;
  padding: 24px;
  min-width: 400px;
  max-width: 90vw;
  border: 1px solid var(--border-color);
}

.pdf-export-modal h2 {
  margin: 0 0 20px 0;
  color: var(--text-heading);
  font-size: 20px;
}

.style-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.style-option {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: var(--input-bg);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-primary);
}

.style-option:hover {
  border-color: var(--accent-gold-1);
  background: var(--hover-bg);
}

.style-option.is-selected {
  border-color: var(--accent-gold-1);
  background: var(--accent-gold-1);
  color: white;
}

.style-icon {
  font-size: 24px;
}

.style-name {
  font-size: 16px;
  font-weight: 500;
}

.cancel-button {
  width: 100%;
  padding: 12px;
  background: var(--button-secondary-bg);
  border: 1px solid var(--button-secondary-border);
  border-radius: 6px;
  color: var(--text-primary);
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-button:hover {
  background: var(--button-secondary-hover);
}
</style>
