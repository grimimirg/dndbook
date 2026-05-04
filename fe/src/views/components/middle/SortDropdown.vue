<template>
  <div class="sort-dropdown-wrapper" ref="dropdownRef">
    <button
        @click="toggleDropdown"
        class="sort-dropdown-button"
        :class="{ 'is-open': isOpen }"
    >
      <span>{{ selectedLabel }}</span>
      <span class="dropdown-arrow">{{ isOpen ? '▲' : '▼' }}</span>
    </button>
    <div v-if="isOpen" class="sort-dropdown-menu">
      <div
          v-for="option in options"
          :key="option.value"
          @click="selectOption(option.value)"
          class="sort-dropdown-item"
          :class="{ 'is-selected': modelValue === option.value }"
      >
        {{ option.label }}
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  options: {
    type: Array,
    required: true
  }
});

const emit = defineEmits(['update:modelValue', 'change']);

const isOpen = ref(false);
const dropdownRef = ref(null);

const selectedLabel = computed(() => {
  const selected = props.options.find(opt => opt.value === props.modelValue);
  return selected ? selected.label : props.options[0].label;
});

function toggleDropdown() {
  isOpen.value = !isOpen.value;
}

function selectOption(value) {
  emit('update:modelValue', value);
  emit('change', value);
  isOpen.value = false;
}

function handleClickOutside(event) {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false;
  }
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
