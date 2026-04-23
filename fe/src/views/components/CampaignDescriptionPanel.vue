<template>
  <div class="campaign-description-panel card flex-col">
    <div v-if="campaignsStore.currentCampaign">
      <div class="panel-header flex-between">
        <h3>{{ t('campaign.descriptionPanel') }}</h3>
        <div v-if="isCurrentCampaignOwned" class="flex-align-center">
          <span
              @click="openEditModal"
              class="edit-description-btn"
              :title="t('campaign.editDescription')"
          >
            🪶
          </span>
          <span
              @click="deleteCampaign"
              :title="t('campaign.deleteTooltip')"
          >
            💀
          </span>
        </div>
      </div>

      <div class="panel-content" :class="{ 'scrollable': isDescriptionLong }">
        <p v-if="campaignsStore.currentCampaign.description" class="description-text">
          {{ campaignsStore.currentCampaign.description }}
        </p>
        <p v-else class="no-description">
          {{ t('campaign.noDescription') }}
        </p>
      </div>
    </div>

    <div v-else class="no-campaign-selected">
      <p class="no-description">{{ t('campaign.selectCampaignChronicle') }}</p>
    </div>

    <CampaignDescriptionEditModal
        :show="showEditModal"
        :description="editedDescription"
        :saving="saving"
        @close="closeEditModal"
        @save="saveDescription"
    />

    <ConfirmModal
        :show="showDeleteConfirm"
        :title="t('campaign.deleteTitle')"
        :message="t('campaign.confirmDelete')"
        @confirm="confirmDelete"
        @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<script setup>
import {computed, ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../stores/campaigns.store.js';
import {useAuthStore} from '../../stores/auth.store.js';
import ConfirmModal from './modals/ConfirmModal.vue';
import CampaignDescriptionEditModal from './modals/CampaignDescriptionEditModal.vue';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const authStore = useAuthStore();

const showEditModal = ref(false);
const editedDescription = ref('');
const saving = ref(false);
const showDeleteConfirm = ref(false);

const isCurrentCampaignOwned = computed(() => {
  if (!campaignsStore.currentCampaign) return false;
  return campaignsStore.ownedCampaigns.some(
      campaign => campaign.id === campaignsStore.currentCampaign.id
  );
});

const isDescriptionLong = computed(() => {
  if (!campaignsStore.currentCampaign?.description) return false;
  return campaignsStore.currentCampaign.description.length > 1000;
});

function openEditModal() {
  editedDescription.value = campaignsStore.currentCampaign.description || '';
  showEditModal.value = true;
}

function closeEditModal() {
  showEditModal.value = false;
  editedDescription.value = '';
}

async function saveDescription(description) {
  saving.value = true;

  const result = await campaignsStore.updateCampaign(
      campaignsStore.currentCampaign.id,
      {description}
  );

  saving.value = false;

  if (result.success) {
    closeEditModal();
  } else {
    alert(result.error || t('common.error'));
  }
}

function deleteCampaign() {
  showDeleteConfirm.value = true;
}

async function confirmDelete() {
  showDeleteConfirm.value = false;
  await campaignsStore.deleteCampaign(campaignsStore.currentCampaign.id);
}
</script>
