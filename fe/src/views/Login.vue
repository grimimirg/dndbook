<template>
  <div class="login-container">
    <div class="top-controls">
      <LanguageSelector />
      <ThemeToggle />
    </div>
    
    <div class="login-wrapper">
      <h1>{{ t('app.title') }}</h1>
      
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

<style scoped>
.top-controls {
  position: absolute;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 12px;
  z-index: 10;
}

.login-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.login-wrapper h1 {
  text-align: center;
  color: var(--text-heading);
  font-size: 32px;
  margin: 0;
}

.toggle {
  margin-top: 50px;
}

.toggle button {
  font-size: 10.5px;
  padding: 6px 12px;
}

.login-card input {
  background: rgba(30, 30, 30, 0.8);
  color: #ffffff;
  border-color: rgba(139, 111, 71, 0.4);
}

.login-card input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.login-card input:focus {
  background: rgba(30, 30, 30, 0.9);
  color: #ffffff;
}
</style>
