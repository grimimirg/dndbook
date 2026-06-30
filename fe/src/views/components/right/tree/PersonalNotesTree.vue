<template>
  <div class="campaign-group">
    <div class="group-title-row flex-between">
      <h3 class="group-title">{{ t('notes.personalNotes') }}</h3>
      <button
        class="menu-toggle-btn"
        :title="t('notes.addNote')"
        @click="handleAddRoot"
      >+</button>
    </div>

    <div v-if="notesStore.loading" class="loading">{{ t('common.loading') }}</div>

    <template v-else>
      <p v-if="rootNotes.length === 0" class="resources-empty">{{ t('notes.noNotes') }}</p>
      <NoteItemTree
        v-for="note in rootNotes"
        :key="note.id"
        :note="note"
        :editable="true"
        default-visibility="private"
      />
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useNotesStore } from '../../../../stores/notes.store.js';
import NoteItemTree from './NoteItemTree.vue';

const { t } = useI18n();
const notesStore = useNotesStore();

const rootNotes = computed(() =>
  notesStore.personalNotes.filter(n => n.parent_id === null)
);

async function handleAddRoot() {
  await notesStore.createNote(t('notes.newNote'), 'private', null);
}
</script>

<style scoped>
.group-title-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
