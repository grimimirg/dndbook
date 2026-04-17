<template>
  <select v-model="currentLocale" @change="changeLocale" class="language-selector">
    <option 
      v-for="localeCode in availableLocales" 
      :key="localeCode" 
      :value="localeCode"
    >
      {{ getLocaleName(localeCode) }}
    </option>
  </select>
</template>

<script setup>
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { getAvailableLocales, getLocaleName } from '../config/locales'

const { locale } = useI18n()
const currentLocale = ref(locale.value)
const availableLocales = getAvailableLocales()

watch(locale, (newLocale) => {
  currentLocale.value = newLocale
})

function changeLocale() {
  locale.value = currentLocale.value
  localStorage.setItem('locale', currentLocale.value)
}
</script>

<style scoped>
.language-selector {
  padding: 6px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  background: white;
}

.language-selector:focus {
  outline: none;
  border-color: #1877f2;
}
</style>
