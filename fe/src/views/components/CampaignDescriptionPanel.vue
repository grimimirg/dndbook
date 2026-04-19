<template>
  <div class="campaign-description-panel card">
    <div v-if="campaignsStore.currentCampaign">
      <div class="panel-header">
        <h3>{{ t('campaign.descriptionPanel') }}</h3>
        <button 
          v-if="isCurrentCampaignOwned" 
          @click="openEditModal" 
          class="edit-description-btn primary"
        >
          {{ t('campaign.editDescription') }}
        </button>
      </div>
      
      <div class="panel-content">
        <p v-if="campaignsStore.currentCampaign.description" class="description-text">
          {{ campaignsStore.currentCampaign.description }}
        </p>
        <p v-else class="no-description">
          {{ t('campaign.noDescription') }}
        </p>
      </div>
    </div>
    
    <div v-else class="no-campaign-selected">
      <p class="no-description">{{ t('campaign.selectCampaign') }}</p>
    </div>

    <Teleport to="body">
      <div v-if="showEditModal" class="modal-overlay" @click="closeEditModal">
        <div class="modal-content" @click.stop>
          <button class="modal-close" @click="closeEditModal">×</button>
          
          <h2>{{ t('campaign.editDescription') }}</h2>
          
          <div class="modal-body">
            <div class="form-group">
              <textarea 
                v-model="editedDescription" 
                class="edit-description-textarea"
                :placeholder="t('campaign.description')"
                rows="10"
              />
            </div>
          </div>
          
          <div class="edit-actions">
            <button class="save-button" @click="saveDescription" :disabled="saving">
              {{ saving ? t('common.loading') : t('post.save') }}
            </button>
            <button class="cancel-button" @click="closeEditModal">
              {{ t('post.cancel') }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCampaignsStore } from '../../stores/campaigns.store.js';
import { useAuthStore } from '../../stores/auth.store.js';

const { t } = useI18n();
const campaignsStore = useCampaignsStore();
const authStore = useAuthStore();

const showEditModal = ref(false);
const editedDescription = ref('');
const saving = ref(false);

const isCurrentCampaignOwned = computed(() => {
  if (!campaignsStore.currentCampaign) return false;
  return campaignsStore.ownedCampaigns.some(
    campaign => campaign.id === campaignsStore.currentCampaign.id
  );
});

function openEditModal() {
  editedDescription.value = campaignsStore.currentCampaign.description || '';
  showEditModal.value = true;
  document.body.style.overflow = 'hidden';
}

function closeEditModal() {
  showEditModal.value = false;
  editedDescription.value = '';
  document.body.style.overflow = '';
}

async function saveDescription() {
  saving.value = true;
  
  const result = await campaignsStore.updateCampaign(
    campaignsStore.currentCampaign.id,
    { description: editedDescription.value }
  );
  
  saving.value = false;
  
  if (result.success) {
    closeEditModal();
  } else {
    alert(result.error || t('common.error'));
  }
}
</script>
