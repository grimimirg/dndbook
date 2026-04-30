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

            <div v-if="isCurrentCampaignOwned" class="character-actions" @click.stop>
              <button
                  :ref="el => setButtonRef(character.id, el)"
                  @click="toggleCharacterMenu(character.id, $event)"
                  class="menu-toggle-btn"
                  :title="t('character.actions')"
              >
                ⋮
              </button>
              <Teleport to="body">
                <div
                    v-if="openMenuId === character.id"
                    class="campaign-actions-menu"
                    :style="menuPosition"
                >
                  <button @click="handleEditCharacter(character)" class="menu-item">
                    <span class="menu-icon">🪶</span>
                    <span>{{ t('character.edit') }}</span>
                  </button>
                  <button @click="handleDeleteCharacter(character)" class="menu-item">
                    <span class="menu-icon">💀</span>
                    <span>{{ t('character.delete') }}</span>
                  </button>
                </div>
              </Teleport>
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
import {computed, onMounted, onUnmounted, ref, watch} from 'vue';
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
const openMenuId = ref(null);
const menuPosition = ref({});
const buttonRefs = ref({});

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

function setButtonRef(characterId, el) {
  if (el) {
    buttonRefs.value[characterId] = el;
  }
}

function toggleCharacterMenu(characterId, event) {
  if (openMenuId.value === characterId) {
    openMenuId.value = null;
    menuPosition.value = {};
  } else {
    openMenuId.value = characterId;
    const button = event.currentTarget;
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

function handleEditCharacter(character) {
  openMenuId.value = null;
  openEditModal(character);
}

function handleDeleteCharacter(character) {
  openMenuId.value = null;
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

function handleClickOutside(event) {
  const menuContainer = event.target.closest('.character-actions');
  if (!menuContainer && openMenuId.value !== null) {
    openMenuId.value = null;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});

watch(() => campaignsStore.currentCampaign, (newCampaign) => {
  if (newCampaign) {
    charactersStore.fetchCharacters(newCampaign.id);
  } else {
    charactersStore.$reset();
  }
}, {immediate: true});
</script>
