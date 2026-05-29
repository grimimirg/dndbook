<template>
  <div v-if="show" class="mention-autocomplete" :style="position">
    <div
      v-for="(character, index) in filteredCharacters"
      :key="character.id"
      class="mention-item"
      :class="{ selected: index === selectedIndex }"
      @click="selectCharacter(character)"
      @mouseenter="selectedIndex = index"
    >
      <div v-if="character.image_url" class="character-avatar">
        <img :src="character.image_url" :alt="character.name" loading="lazy" />
      </div>
      <div v-else class="character-avatar placeholder">
        {{ character.name.charAt(0) }}
      </div>
      <div class="character-info">
        <div class="character-name">{{ character.name }}</div>
        <div class="character-details">
          {{ character.race }} • {{ character.character_class }}
        </div>
      </div>
    </div>
    <div v-if="filteredCharacters.length === 0" class="mention-item no-results">
      {{ t('post.noCharactersFound') }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCharactersStore } from '../../stores/characters.store.js';

const props = defineProps({
  show: Boolean,
  query: String,
  campaignId: Number,
  textareaRef: Object
});

const emit = defineEmits(['select', 'close']);

const { t } = useI18n();
const charactersStore = useCharactersStore();

const filteredCharacters = ref([]);
const selectedIndex = ref(0);
const position = ref({ top: '0px', left: '0px' });

watch(() => props.show, async (newVal) => {
  if (newVal && props.query && props.campaignId) {
    await searchCharacters();
    await updatePosition();
  } else {
    filteredCharacters.value = [];
  }
});

watch(() => props.query, async () => {
  if (props.show && props.query && props.campaignId) {
    await searchCharacters();
    selectedIndex.value = 0;
  }
});

async function searchCharacters() {
  if (!props.query || props.query.length < 1) {
    filteredCharacters.value = [];
    return;
  }

  const result = await charactersStore.searchCharacters(props.campaignId, props.query);
  if (result.success) {
    filteredCharacters.value = result.characters;
  } else {
    filteredCharacters.value = [];
  }
}

async function updatePosition() {
  if (!props.textareaRef) return;

  await nextTick();

  const textarea = props.textareaRef;
  const rect = textarea.getBoundingClientRect();
  const cursorPosition = textarea.selectionStart;

  // Calculate cursor position within the textarea
  const textBeforeCursor = textarea.value.substring(0, cursorPosition);
  const lines = textBeforeCursor.split('\n');
  const currentLineIndex = lines.length - 1;
  const currentLineText = lines[currentLineIndex];

  // Create a temporary span to measure text width
  const span = document.createElement('span');
  const computedStyle = window.getComputedStyle(textarea);
  span.style.font = computedStyle.font;
  span.style.fontSize = computedStyle.fontSize;
  span.style.fontFamily = computedStyle.fontFamily;
  span.style.whiteSpace = 'pre';
  span.style.visibility = 'hidden';
  span.style.position = 'absolute';
  span.textContent = currentLineText;
  document.body.appendChild(span);
  const textWidth = span.offsetWidth;
  document.body.removeChild(span);

  // Calculate line height
  const lineHeightStyle = computedStyle.lineHeight;
  const lineHeight = lineHeightStyle === 'normal' 
    ? parseInt(computedStyle.fontSize) * 1.2 
    : parseInt(lineHeightStyle);
  
  const paddingLeft = parseInt(computedStyle.paddingLeft) || 0;
  const paddingTop = parseInt(computedStyle.paddingTop) || 0;

  // Calculate position based on cursor (use fixed positioning relative to viewport)
  const cursorX = rect.left + paddingLeft + textWidth;
  const cursorY = rect.top + paddingTop + (currentLineIndex * lineHeight) + lineHeight + 4;

  position.value = {
    top: `${cursorY}px`,
    left: `${cursorX}px`
  };
}

function selectCharacter(character) {
  emit('select', character);
  emit('close');
}

function handleKeydown(event) {
  if (!props.show) return;

  if (event.key === 'ArrowDown') {
    event.preventDefault();
    selectedIndex.value = Math.min(selectedIndex.value + 1, filteredCharacters.value.length - 1);
  } else if (event.key === 'ArrowUp') {
    event.preventDefault();
    selectedIndex.value = Math.max(selectedIndex.value - 1, 0);
  } else if (event.key === 'Enter') {
    event.preventDefault();
    if (filteredCharacters.value[selectedIndex.value]) {
      selectCharacter(filteredCharacters.value[selectedIndex.value]);
    }
  } else if (event.key === 'Escape') {
    event.preventDefault();
    emit('close');
  }
}

defineExpose({
  handleKeydown
});
</script>
