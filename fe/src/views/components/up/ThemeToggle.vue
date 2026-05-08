<template>
  <button @click="toggleTheme" class="theme-toggle btn-circle btn-circle-lg" :title="currentTheme === ThemeTypes.DARK ? 'Switch to Light Theme' : 'Switch to Dark Theme'">
    <span v-if="currentTheme === ThemeTypes.DARK">☀️</span>
    <span v-else>🌙</span>
  </button>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { ThemeTypes } from '@/constants/themeConstants';

const currentTheme = ref(ThemeTypes.DARK);

onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || ThemeTypes.DARK;
  currentTheme.value = savedTheme;
  applyTheme(savedTheme);
});

watch(currentTheme, (newTheme) => {
  applyTheme(newTheme);
});

function toggleTheme() {
  const newTheme = currentTheme.value === ThemeTypes.DARK ? ThemeTypes.LIGHT : ThemeTypes.DARK;
  currentTheme.value = newTheme;
  applyTheme(newTheme);
  localStorage.setItem('theme', newTheme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
}
</script>
