<template>
  <Teleport to="body">
    <div v-if="show" class="modal-overlay" @click="handleClose">
      <div class="modal-content character-selection-modal" @click.stop>
        <h3>{{ t('character.selectCharacter') }}</h3>
        <br>

        <div v-if="loading" class="loading">
          {{ t('common.loading') }}
        </div>

        <div v-else-if="characters.length === 0" class="empty-state">
          {{ t('character.noPredefinedCharacters') }}
        </div>

        <div v-else class="characters-grid">
          <div
            v-for="character in characters"
            :key="character.id"
            class="character-card"
            :class="{ 'selected': selectedCharacterId === character.id, 'assigned': character.assigned_to_user_id }"
            @click="handleCharacterClick(character)"
          >
            <div v-if="character.image_url" class="character-image">
              <img :src="character.image_url" :alt="character.name" loading="lazy"/>
            </div>
            <div class="character-info">
              <div class="character-name">{{ character.name }}</div>
              <div class="character-details">
                <span class="character-race">{{ character.race }}</span>
                <span class="character-class">{{ character.character_class }}</span>
              </div>
              <div v-if="character.description" class="character-description">
                {{ character.description }}
              </div>
              <div v-if="character.assigned_to_user_id" class="character-assigned">
                {{ t('character.assigned') }}
              </div>
            </div>
          </div>
        </div>

        <div class="modal-actions">
          <button type="button" @click="handleClose" class="secondary">
            {{ t('common.cancel') }}
          </button>
          <button
            type="button"
            @click="handleConfirm"
            class="primary"
            :disabled="!selectedCharacterId || !!selectedCharacter?.assigned_to_user_id"
          >
            {{ selecting ? t('common.loading') : t('common.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCharactersStore } from '../../../stores/characters.store.js';

const { t } = useI18n();
const charactersStore = useCharactersStore();

const props = defineProps({
  show: Boolean,
  campaignId: Number
});

const emit = defineEmits(['close', 'success']);

const characters = ref([]);
const loading = ref(false);
const selectedCharacterId = ref(null);
const selecting = ref(false);

const selectedCharacter = computed(() => 
  characters.value.find(c => c.id === selectedCharacterId.value)
);

watch(() => props.show, async (newVal) => {
  if (newVal && props.campaignId) {
    await fetchCharacters();
  } else {
    resetForm();
  }
  if (newVal) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
});

async function fetchCharacters() {
  loading.value = true;
  try {
    const result = await charactersStore.fetchPredefinedCharacters(props.campaignId);
    if (result.success) {
      characters.value = result.characters.filter(c => !c.assigned_to_user_id);
    }
  } catch (error) {
    console.error('Failed to fetch predefined characters:', error);
  } finally {
    loading.value = false;
  }
}

function resetForm() {
  characters.value = [];
  selectedCharacterId.value = null;
  selecting.value = false;
}

function handleCharacterClick(character) {
  if (!character.assigned_to_user_id) {
    selectedCharacterId.value = character.id;
  }
}

async function handleConfirm() {
  if (!selectedCharacterId.value || selectedCharacter.value?.assigned_to_user_id) {
    return;
  }

  selecting.value = true;
  try {
    const result = await charactersStore.assignCharacterToUser(
      props.campaignId,
      selectedCharacterId.value,
      null // Assign to current user
    );
    if (result.success) {
      emit('success');
      resetForm();
    } else {
      alert(result.error || t('common.error'));
    }
  } catch (error) {
    console.error('Failed to assign character:', error);
    alert(t('common.error'));
  } finally {
    selecting.value = false;
  }
}

function handleClose() {
  resetForm();
  emit('close');
}
</script>
