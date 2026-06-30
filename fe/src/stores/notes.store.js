import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '../services/api.service.js';
import { useAuthStore } from './auth.store.js';

export const useNotesStore = defineStore('notes', () => {
  const notes = ref([]);
  const loading = ref(false);

  const personalNotes = computed(() => {
    const authStore = useAuthStore();
    return notes.value.filter(n => n.owner_id === authStore.user?.id);
  });

  const playerNotes = computed(() => {
    const authStore = useAuthStore();
    return notes.value.filter(n => n.owner_id !== authStore.user?.id && n.visibility === 'public');
  });

  function childrenOf(parentId) {
    return notes.value.filter(n => n.parent_id === parentId);
  }

  async function fetchNotes() {
    loading.value = true;
    try {
      const response = await api.get('/notes');
      notes.value = response.data;
    } catch (error) {
      console.error('Failed to fetch notes:', error);
    } finally {
      loading.value = false;
    }
  }

  async function createNote(title, visibility = 'private', parentId = null) {
    try {
      const response = await api.post('/notes', { title, visibility, parent_id: parentId });
      notes.value.push(response.data);
      return { success: true, note: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to create note' };
    }
  }

  async function updateNote(id, data) {
    try {
      const response = await api.put(`/notes/${id}`, data);
      const idx = notes.value.findIndex(n => n.id === id);
      if (idx !== -1) notes.value[idx] = response.data;
      return { success: true, note: response.data };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to update note' };
    }
  }

  async function deleteNote(id) {
    try {
      await api.delete(`/notes/${id}`);
      const toRemove = collectDescendants(id);
      notes.value = notes.value.filter(n => !toRemove.has(n.id));
      return { success: true };
    } catch (error) {
      return { success: false, error: error.response?.data?.error || 'Failed to delete note' };
    }
  }

  function collectDescendants(noteId) {
    const result = new Set([noteId]);
    const queue = [noteId];
    while (queue.length > 0) {
      const current = queue.shift();
      notes.value
        .filter(n => n.parent_id === current)
        .forEach(c => { result.add(c.id); queue.push(c.id); });
    }
    return result;
  }

  function $reset() {
    notes.value = [];
    loading.value = false;
  }

  return {
    notes,
    loading,
    personalNotes,
    playerNotes,
    childrenOf,
    fetchNotes,
    createNote,
    updateNote,
    deleteNote,
    $reset
  };
});
