<template>
  <div class="predefined-characters-manager">
    <div class="manager-header">
      <h4>{{ t('character.predefinedCharacters') }}</h4>
      <button @click="showCreateModal = true" class="primary btn-sm">
        {{ t('character.createPredefined') }}
      </button>
    </div>

    <div v-if="loading" class="loading">
      {{ t('common.loading') }}
    </div>

    <div v-else-if="characters.length === 0" class="empty-state">
      {{ t('character.noPredefinedCharacters') }}
    </div>

    <div v-else class="characters-list">
      <div
        v-for="character in characters"
        :key="character.id"
        class="character-item"
      >
        <div class="character-info">
          <div class="character-image" v-if="character.image_url">
            <img :src="character.image_url" :alt="character.name"/>
          </div>
          <div class="character-details">
            <div class="character-name">{{ character.name }}</div>
            <div class="character-meta">
              <span>{{ character.race }}</span> • <span>{{ character.character_class }}</span>
            </div>
            <div v-if="character.assigned_to_user_id" class="assigned-badge">
              {{ t('character.assignedTo') }}
            </div>
            <div v-else class="available-badge">
              {{ t('character.available') }}
            </div>
          </div>
        </div>
        <div class="character-actions">
          <button
            v-if="!character.assigned_to_user_id"
            @click="handleEdit(character)"
            class="secondary btn-sm"
          >
            {{ t('common.edit') }}
          </button>
          <button
            v-if="!character.assigned_to_user_id"
            @click="handleDelete(character)"
            class="danger btn-sm"
          >
            {{ t('common.delete') }}
          </button>
          <button
            v-if="character.assigned_to_user_id"
            @click="handleUnassign(character)"
            class="secondary btn-sm"
          >
            {{ t('character.unassign') }}
          </button>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <CreateCharacterModal
      v-if="showCreateModal"
      :show="showCreateModal"
      :campaign-id="campaignId"
      :character="editingCharacter"
      @close="handleCloseModal"
      @success="handleCharacterSuccess"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCharactersStore } from '../../../../stores/characters.store.js';
import CreateCharacterModal from './CreateCharacterModal.vue';

const { t } = useI18n();
const charactersStore = useCharactersStore();

const props = defineProps({
  campaignId: {
    type: Number,
    required: true
  }
});

const characters = ref([]);
const loading = ref(false);
const showCreateModal = ref(false);
const editingCharacter = ref(null);

onMounted(async () => {
  await fetchCharacters();
});

async function fetchCharacters() {
  loading.value = true;
  try {
    const result = await charactersStore.fetchPredefinedCharacters(props.campaignId);
    if (result.success) {
      characters.value = result.characters;
    }
  } catch (error) {
    console.error('Failed to fetch predefined characters:', error);
  } finally {
    loading.value = false;
  }
}

function handleEdit(character) {
  editingCharacter.value = character;
  showCreateModal.value = true;
}

async function handleDelete(character) {
  if (!confirm(t('character.confirmDelete'))) {
    return;
  }

  try {
    const result = await charactersStore.deleteCharacter(props.campaignId, character.id);
    if (result.success) {
      characters.value = characters.value.filter(c => c.id !== character.id);
    } else {
      alert(result.error || t('common.error'));
    }
  } catch (error) {
    console.error('Failed to delete character:', error);
    alert(t('common.error'));
  }
}

async function handleUnassign(character) {
  if (!confirm(t('character.confirmUnassign'))) {
    return;
  }

  try {
    const result = await charactersStore.unassignCharacter(character.id);
    if (result.success) {
      // Refresh the list
      await fetchCharacters();
    } else {
      alert(result.error || t('common.error'));
    }
  } catch (error) {
    console.error('Failed to unassign character:', error);
    alert(t('common.error'));
  }
}

function handleCloseModal() {
  showCreateModal.value = false;
  editingCharacter.value = null;
}

async function handleCharacterSuccess() {
  handleCloseModal();
  await fetchCharacters();
}
</script>
