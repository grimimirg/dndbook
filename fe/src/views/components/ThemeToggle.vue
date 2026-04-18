<template>
  <button @click="toggleTheme" class="theme-toggle" :title="currentTheme === 'dark' ? 'Switch to Light Theme' : 'Switch to Dark Theme'">
    <span v-if="currentTheme === 'dark'">☀️</span>
    <span v-else>🌙</span>
  </button>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';

const currentTheme = ref('dark');

onMounted(() => {
  const savedTheme = localStorage.getItem('theme') || 'dark';
  currentTheme.value = savedTheme;
  applyTheme(savedTheme);
});

function toggleTheme() {
  const newTheme = currentTheme.value === 'dark' ? 'light' : 'dark';
  currentTheme.value = newTheme;
  applyTheme(newTheme);
  localStorage.setItem('theme', newTheme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
}

watch(currentTheme, (newTheme) => {
  applyTheme(newTheme);
});
</script>
