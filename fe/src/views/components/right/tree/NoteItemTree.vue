<template>
  <div class="note-node">
    <div
      class="campaign-header flex-align-center"
      :class="{ active: expanded }"
      @click="toggleExpand"
    >
      <span class="expand-icon">{{ expanded ? '▼' : '▶' }}</span>

      <input
        v-if="isRenaming"
        ref="renameInput"
        v-model="newTitle"
        class="note-rename-input"
        @keyup.enter="confirmRename"
        @keyup.escape="cancelRename"
        @blur="confirmRename"
        @click.stop
      />
      <span v-else class="campaign-name">{{ note.title }}</span>

      <div v-if="editable" class="campaign-menu-container">
        <button
          :ref="el => { menuButtonEl = el }"
          class="menu-toggle-btn"
          :title="t('notes.actions')"
          @click.stop="toggleMenu($event)"
        >⋮</button>
        <Teleport to="body">
          <div
            v-if="showMenu"
            class="campaign-actions-menu"
            :style="menuPosition"
          >
            <button class="menu-item" @click.stop="handleAddChild">
              <span class="menu-icon">+</span>
              <span>{{ t('notes.addChild') }}</span>
            </button>
            <button class="menu-item" @click.stop="handleRename">
              <span class="menu-icon">✏</span>
              <span>{{ t('notes.rename') }}</span>
            </button>
            <button class="menu-item" @click.stop="handleDeleteClick">
              <span class="menu-icon">✕</span>
              <span>{{ t('notes.delete') }}</span>
            </button>
          </div>
        </Teleport>
      </div>
    </div>

    <div v-if="expanded" class="note-expanded">
      <textarea
        v-if="editable"
        v-model="editedContent"
        class="note-content-textarea"
        :placeholder="t('notes.contentPlaceholder')"
        @blur="saveContent"
        @click.stop
      />
      <pre v-else-if="note.content" class="note-content-view">{{ note.content }}</pre>

      <div class="note-children">
        <NoteItemTree
          v-for="child in children"
          :key="child.id"
          :note="child"
          :editable="editable"
          :default-visibility="defaultVisibility"
        />
      </div>
    </div>
  </div>

  <ConfirmModal
    :show="showDeleteConfirm"
    :title="t('notes.deleteTitle')"
    :message="t('notes.confirmDelete')"
    @confirm="confirmDelete"
    @cancel="showDeleteConfirm = false"
  />
</template>

<script>
export default { name: 'NoteItemTree' }
</script>

<script setup>
import { ref, computed, nextTick, onMounted, onUnmounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useNotesStore } from '../../../../stores/notes.store.js';
import ConfirmModal from '../../modals/ConfirmModal.vue';

const { t } = useI18n();
const notesStore = useNotesStore();

const props = defineProps({
  note: { type: Object, required: true },
  editable: { type: Boolean, default: false },
  defaultVisibility: { type: String, default: 'private' }
});

const expanded = ref(false);
const isRenaming = ref(false);
const newTitle = ref('');
const renameInput = ref(null);
const editedContent = ref('');
const showMenu = ref(false);
const menuPosition = ref({});
const menuButtonEl = ref(null);
const showDeleteConfirm = ref(false);

const children = computed(() => notesStore.childrenOf(props.note.id));

function toggleExpand() {
  if (isRenaming.value) return;
  expanded.value = !expanded.value;
  if (expanded.value) {
    editedContent.value = props.note.content || '';
  }
}

function toggleMenu(event) {
  if (showMenu.value) {
    showMenu.value = false;
    return;
  }
  const rect = event.currentTarget.getBoundingClientRect();
  menuPosition.value = {
    top: `${rect.bottom + 8}px`,
    left: `${rect.right - 160}px`
  };
  showMenu.value = true;
}

function handleClickOutside(event) {
  const menuContainer = event.target.closest('.campaign-menu-container');
  if (!menuContainer && showMenu.value) {
    showMenu.value = false;
  }
}

onMounted(() => document.addEventListener('click', handleClickOutside));
onUnmounted(() => document.removeEventListener('click', handleClickOutside));

async function handleAddChild() {
  showMenu.value = false;
  expanded.value = true;
  await notesStore.createNote(t('notes.newNote'), props.defaultVisibility, props.note.id);
}

function handleRename() {
  showMenu.value = false;
  isRenaming.value = true;
  newTitle.value = props.note.title;
  nextTick(() => renameInput.value?.focus());
}

async function confirmRename() {
  if (newTitle.value.trim() && newTitle.value.trim() !== props.note.title) {
    await notesStore.updateNote(props.note.id, { title: newTitle.value.trim() });
  }
  isRenaming.value = false;
}

function cancelRename() {
  isRenaming.value = false;
}

async function saveContent() {
  if (editedContent.value !== (props.note.content || '')) {
    await notesStore.updateNote(props.note.id, { content: editedContent.value });
  }
}

function handleDeleteClick() {
  showMenu.value = false;
  showDeleteConfirm.value = true;
}

async function confirmDelete() {
  showDeleteConfirm.value = false;
  await notesStore.deleteNote(props.note.id);
}
</script>

<style scoped>
.note-node {
  width: 100%;
}

.note-expanded {
  padding-left: 20px;
}

.note-rename-input {
  flex: 1;
  background: transparent;
  border: none;
  border-bottom: 1px solid var(--border-color, #555);
  color: inherit;
  font: inherit;
  font-size: 0.9rem;
  outline: none;
  padding: 0 4px;
  min-width: 0;
}

.note-content-textarea {
  width: 100%;
  min-height: 80px;
  background: var(--input-bg, rgba(255,255,255,0.05));
  border: 1px solid var(--border-color, #555);
  border-radius: 4px;
  color: inherit;
  font-family: monospace;
  font-size: 0.85rem;
  padding: 6px 8px;
  resize: vertical;
  box-sizing: border-box;
  margin-top: 4px;
  margin-bottom: 4px;
}

.note-content-view {
  font-family: monospace;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-break: break-word;
  padding: 6px 8px;
  margin: 4px 0;
  background: var(--input-bg, rgba(255,255,255,0.03));
  border-radius: 4px;
  border: 1px solid var(--border-color, #444);
}

.note-children {
  margin-top: 2px;
}
</style>
