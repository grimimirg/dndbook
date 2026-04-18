<template>
  <div class="login-container">
    <div class="top-controls">
      <LanguageSelector />
      <ThemeToggle />
    </div>
    
    <div class="login-wrapper">
      <img src="/images/dnd-book-logo.png" alt="D&D Book" class="logo" />
      
      <div class="login-card">
        <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <input 
            v-model="username" 
            type="text" 
            :placeholder="t('auth.username')" 
            required
          />
        </div>
        
        <div class="form-group" v-if="isRegister">
          <input 
            v-model="email" 
            type="email" 
            :placeholder="t('auth.email')" 
            required
          />
        </div>
        
        <div class="form-group">
          <input 
            v-model="password" 
            type="password" 
            :placeholder="t('auth.password')" 
            required
          />
        </div>
        
        <div v-if="error" class="error">{{ error }}</div>
        
        <button type="submit" class="primary" :disabled="loading">
          {{ loading ? t('common.loading') : (isRegister ? t('auth.register') : t('auth.login')) }}
        </button>
      </form>
      
      <div class="toggle">
        <button @click="isRegister = !isRegister" class="secondary">
          {{ isRegister ? t('auth.alreadyHaveAccount') : t('auth.needAccount') }}
        </button>
      </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'
import LanguageSelector from '../components/LanguageSelector.vue'
import ThemeToggle from '../components/ThemeToggle.vue'

const router = useRouter()
const { t } = useI18n()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const isRegister = ref(false)
const loading = ref(false)
const error = ref('')

async function handleSubmit() {
  loading.value = true
  error.value = ''
  
  let result
  if (isRegister.value) {
    result = await authStore.register(username.value, email.value, password.value)
  } else {
    result = await authStore.login(username.value, password.value)
  }
  
  loading.value = false
  
  if (result.success) {
    router.push('/')
  } else {
    error.value = result.error
  }
}
</script>
