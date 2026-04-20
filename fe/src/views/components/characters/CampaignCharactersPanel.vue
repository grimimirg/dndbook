<template>
  <div class="campaign-characters-panel card flex-col">
    <div v-if="campaignsStore.currentCampaign">
      <div class="panel-header flex-between">
        <h3>{{ t('character.characters') }}</h3>
        <span
            v-if="isCurrentCampaignOwned"
            @click="openCreateModal"
            class="btn-circle"
            :title="t('character.createTooltip')"
        >
          +
        </span>
      </div>
      <br>

      <div class="panel-content">
        <div v-if="charactersStore.loading" class="loading flex-center">
          {{ t('common.loading') }}
        </div>

        <div v-else-if="charactersStore.characters.length === 0" class="empty-message">
          <p>{{ t('character.noCharacters') }}</p>
          <p v-if="isCurrentCampaignOwned" class="hint">{{ t('character.noCharactersHint') }}</p>
        </div>

        <div v-else class="characters-list flex-col">
          <div
              v-for="character in charactersStore.characters"
              :key="character.id"
              class="character-item flex-align-center"
              @click="openDetailModal(character)"
          >
            <div class="character-portrait">
              <img
                  v-if="character.image_url"
                  :src="getImageUrl(character.image_url)"
                  :alt="character.name"
              />
              <div v-else class="no-image">?</div>
            </div>

            <div class="character-info flex-col">
              <span class="character-name">{{ character.name }}</span>
              <span class="character-race">{{ character.race }}</span>
              <span class="character-class">{{ character.character_class }}</span>
            </div>

            <div v-if="isCurrentCampaignOwned" class="character-actions flex-align-center" @click.stop>
              <button
                  @click="openEditModal(character)"
                  class="edit-btn"
                  :title="t('character.edit')"
              >
                🪶
              </button>
              <button
                  @click="handleDeleteCharacter(character)"
                  class="delete-btn"
                  :title="t('character.delete')"
              >
                💀
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="no-campaign-selected">
      <p class="no-description">{{ t('campaign.selectCampaignChronicle') }}</p>
    </div>

    <CreateCharacterModal
        :show="showCreateModal"
        :character="characterToEdit"
        :campaign-id="campaignsStore.currentCampaign?.id"
        @close="closeCreateModal"
        @success="handleCharacterSaved"
    />

    <CharacterDetailModal
        :show="showDetailModal"
        :character="selectedCharacter"
        @close="closeDetailModal"
    />

    <ConfirmModal
        :show="showDeleteConfirm"
        :title="t('character.deleteTitle')"
        :message="t('character.confirmDelete')"
        @confirm="confirmDelete"
        @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<script setup>
import {computed, ref, watch} from 'vue';
import {useI18n} from 'vue-i18n';
import {useCampaignsStore} from '../../../stores/campaigns.store.js';
import {useCharactersStore} from '../../../stores/characters.store.js';
import {useAuthStore} from '../../../stores/auth.store.js';
import CreateCharacterModal from './CreateCharacterModal.vue';
import CharacterDetailModal from './CharacterDetailModal.vue';
import ConfirmModal from '../modals/ConfirmModal.vue';
import config from '../../../config/config.js';

const {t} = useI18n();
const campaignsStore = useCampaignsStore();
const charactersStore = useCharactersStore();
const authStore = useAuthStore();

const showCreateModal = ref(false);
const showDetailModal = ref(false);
const showDeleteConfirm = ref(false);
const characterToEdit = ref(null);
const selectedCharacter = ref(null);
const characterToDelete = ref(null);

const isCurrentCampaignOwned = computed(() => {
  if (!campaignsStore.currentCampaign) return false;
  return campaignsStore.ownedCampaigns.some(
      campaign => campaign.id === campaignsStore.currentCampaign.id
  );
});

function getImageUrl(imageUrl) {
  if (!imageUrl) return '';
  if (imageUrl.startsWith('http')) return imageUrl;
  return `${config.API_BASE_URL}${imageUrl}`;
}

function getDescriptionPreview(description) {
  if (!description) return '';
  return description.length > 20 ? description.substring(0, 20) + '...' : description;
}

function openCreateModal() {
  characterToEdit.value = null;
  showCreateModal.value = true;
}

function openEditModal(character) {
  characterToEdit.value = character;
  showCreateModal.value = true;
}

function closeCreateModal() {
  showCreateModal.value = false;
  characterToEdit.value = null;
}

function openDetailModal(character) {
  selectedCharacter.value = character;
  showDetailModal.value = true;
}

function closeDetailModal() {
  showDetailModal.value = false;
  selectedCharacter.value = null;
}

function handleCharacterSaved() {
  closeCreateModal();
  charactersStore.fetchCharacters(campaignsStore.currentCampaign.id);
}

function handleDeleteCharacter(character) {
  characterToDelete.value = character;
  showDeleteConfirm.value = true;
}

async function confirmDelete() {
  showDeleteConfirm.value = false;
  if (characterToDelete.value && campaignsStore.currentCampaign) {
    const result = await charactersStore.deleteCharacter(
        campaignsStore.currentCampaign.id,
        characterToDelete.value.id
    );
    if (!result.success) {
      alert(result.error || t('common.error'));
    }
  }
  characterToDelete.value = null;
}

watch(() => campaignsStore.currentCampaign, (newCampaign) => {
  if (newCampaign) {
    charactersStore.fetchCharacters(newCampaign.id);
  } else {
    charactersStore.$reset();
  }
}, {immediate: true});
</script>
