<template>
  <div class="login-container">
    <div class="login-card">
      <div class="language-selector-container">
        <select v-model="currentLocale" @change="changeLocale" class="language-selector">
          <option value="en">English</option>
          <option value="it">Italiano</option>
          <option value="de">Deutsch</option>
        </select>
      </div>
      
      <h1>{{ t('app.title') }}</h1>
      
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
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const { locale, t } = useI18n()
const authStore = useAuthStore()

const username = ref('')
const email = ref('')
const password = ref('')
const isRegister = ref(false)
const loading = ref(false)
const error = ref('')
const currentLocale = ref(locale.value)

function changeLocale() {
  locale.value = currentLocale.value
  localStorage.setItem('locale', currentLocale.value)
}

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
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f0f2f5;
}

.login-card {
  background: white;
  padding: 40px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 400px;
}

.language-selector-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 20px;
}

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

h1 {
  text-align: center;
  margin-bottom: 30px;
  color: #1877f2;
}

.form-group {
  margin-bottom: 16px;
}

.error {
  color: #d93025;
  font-size: 14px;
  margin-bottom: 16px;
  padding: 8px;
  background-color: #fce8e6;
  border-radius: 4px;
}

button[type="submit"] {
  width: 100%;
  padding: 12px;
  font-size: 16px;
}

.toggle {
  margin-top: 16px;
  text-align: center;
}

.toggle button {
  width: 100%;
}
</style>
