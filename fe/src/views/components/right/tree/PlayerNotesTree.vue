<template>
  <div v-if="notesStore.playerNotes.length > 0 || notesStore.loading" class="campaign-group">
    <h3 class="group-title">{{ t('notes.playerNotes') }}</h3>

    <div v-if="notesStore.loading" class="loading">{{ t('common.loading') }}</div>

    <template v-else>
      <p v-if="rootNotes.length === 0" class="resources-empty">{{ t('notes.noNotes') }}</p>
      <NoteItemTree
        v-for="note in rootNotes"
        :key="note.id"
        :note="note"
        :editable="false"
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
  notesStore.playerNotes.filter(n => n.parent_id === null)
);
</script>
