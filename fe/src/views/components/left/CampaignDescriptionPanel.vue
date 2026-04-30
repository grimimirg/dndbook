<template>
  <div class="campaign-description-panel card flex-col">
    <div v-if="campaignsStore.currentCampaign">
      <div class="panel-header flex-between">
        <h3>{{ t('campaign.descriptionPanel') }}</h3>
        <div v-if="isCurrentCampaignOwned" class="campaign-description-menu-container">
          <button
              ref="descriptionMenuButton"
              @click="toggleDescriptionMenu"
              class="menu-toggle-btn"
              :title="t('campaign.actions')"
          >
            ⋮
          </button>
          <Teleport to="body">
            <div v-if="showActionsMenu" class="campaign-actions-menu" :style="menuPosition">
              <button @click="handleEditDescription" class="menu-item">
                <span class="menu-icon">🪶</span>
                <span>{{ t('campaign.editDescription') }}</span>
              </button>
              <button @click="handleDeleteCampaign" class="menu-item">
                <span class="menu-icon">💀</span>
                <span>{{ t('campaign.delete') }}</span>
              </button>
            </div>
          </Teleport>
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
import {computed, onMounted, onUnmounted, ref} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../../stores/campaigns.store.js';
import {useAuthStore} from '../../../stores/auth.store.js';
import ConfirmModal from '../modals/ConfirmModal.vue';
import CampaignDescriptionEditModal from '../modals/CampaignDescriptionEditModal.vue';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const authStore = useAuthStore();

const showEditModal = ref(false);
const editedDescription = ref('');
const saving = ref(false);
const showDeleteConfirm = ref(false);
const showActionsMenu = ref(false);
const menuPosition = ref({});
const descriptionMenuButton = ref(null);

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

function toggleDescriptionMenu() {
  if (showActionsMenu.value) {
    showActionsMenu.value = false;
    menuPosition.value = {};
  } else {
    showActionsMenu.value = true;
    const button = descriptionMenuButton.value;
    if (button) {
      const rect = button.getBoundingClientRect();
      const menuWidth = 200;
      const viewportWidth = window.innerWidth;
      
      let left = rect.right - menuWidth;
      
      if (left < 8) {
        left = 8;
      }
      
      if (left + menuWidth > viewportWidth - 8) {
        left = viewportWidth - menuWidth - 8;
      }
      
      const top = rect.bottom + 8;
      
      menuPosition.value = {
        top: `${top}px`,
        left: `${left}px`,
        right: 'auto'
      };
    }
  }
}

function handleEditDescription() {
  showActionsMenu.value = false;
  openEditModal();
}

function handleDeleteCampaign() {
  showActionsMenu.value = false;
  deleteCampaign();
}

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

function handleClickOutside(event) {
  const menuContainer = event.target.closest('.campaign-description-menu-container');
  if (!menuContainer && showActionsMenu.value) {
    showActionsMenu.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
