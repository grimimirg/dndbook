<template>
  <div class="user-profile-customization">
    <div class="modal-overlay" @click="closeModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ t('profile.title') }}</h2>
          <div class="header-controls flex-align-center">
            <ThemeToggle/>
            <button @click="closeModal" class="close-btn">×</button>
          </div>
        </div>

        <div class="modal-body">
          <!-- Avatar Section -->
          <div class="profile-section">
            <h3>{{ t('profile.avatar') }}</h3>
            <div class="avatar-section">
              <div class="avatar-preview">
                <img v-if="formData.avatar_url || authStore.user?.avatar_url" 
                     :src="getAvatarUrl(formData.avatar_url || authStore.user?.avatar_url)" 
                     :alt="t('profile.avatar')"
                     class="avatar-image" loading="lazy" />
                <div v-else class="avatar-placeholder">
                  {{ (authStore.user?.nickname || authStore.user?.username || 'U').charAt(0).toUpperCase() }}
                </div>
              </div>
              <div class="avatar-actions">
                <input type="file" ref="avatarInput" accept="image/png,image/jpeg,image/gif,image/webp" 
                       @change="handleAvatarUpload" class="hidden-file-input" />
                <button @click="$refs.avatarInput.click()" class="secondary">
                  {{ t('profile.uploadAvatar') }}
                </button>
                <button v-if="formData.avatar_url || authStore.user?.avatar_url" 
                        @click="removeAvatar" class="secondary">
                  {{ t('profile.removeAvatar') }}
                </button>
              </div>
            </div>
          </div>

          <!-- Nickname Section -->
          <div class="profile-section">
            <h3>{{ t('profile.nickname') }}</h3>
            <input v-model="formData.nickname" 
                   type="text" 
                   :placeholder="t('profile.nicknamePlaceholder')"
                   class="profile-input" />
          </div>

          <div class="profile-section">
            <h3>{{ t('profile.applicationLanguage') }}</h3>
            <LanguageSelector/>
          </div>

          <!-- Performance Mode Section -->
          <div class="profile-section">
            <h3>{{ t('profile.performanceMode') }}</h3>
            <div class="performance-mode-toggle flex-align-center">
              <input 
                type="checkbox" 
                id="performance-mode" 
                v-model="performanceMode" 
                @change="handlePerformanceModeToggle"
                class="performance-checkbox"
              />
              <label for="performance-mode" class="performance-label">
                {{ t('profile.performanceModeDescription') }}
              </label>
            </div>
          </div>

          <!-- Biography Section -->
          <div class="profile-section">
            <h3>{{ t('profile.biography') }}</h3>
            <textarea v-model="formData.biography" 
                      :placeholder="t('profile.biographyPlaceholder')"
                      class="profile-textarea"
                      rows="4" />
          </div>

          <!-- Password Section -->
          <div class="profile-section">
            <h3>{{ t('profile.changePassword') }}</h3>
            <div class="password-fields">
              <input v-model="passwordData.currentPassword" 
                     type="password" 
                     :placeholder="t('profile.currentPassword')"
                     class="profile-input" />
              <input v-model="passwordData.newPassword" 
                     type="password" 
                     :placeholder="t('profile.newPassword')"
                     class="profile-input" />
              <input v-model="passwordData.confirmPassword" 
                     type="password" 
                     :placeholder="t('profile.confirmPassword')"
                     class="profile-input" />
            </div>
            <button @click="updatePassword" class="secondary password-btn">
              {{ t('profile.updatePassword') }}
            </button>
          </div>
        </div>

        <div class="modal-footer">
          <button @click="saveProfile" class="primary" :disabled="userStore.isSaving">
            {{ userStore.isSaving ? t('profile.saving') : t('profile.save') }}
          </button>
          <button @click="closeModal" class="secondary">
            {{ t('common.cancel') }}
          </button>
        </div>
      </div>
    </div>
    <ToastNotification
      :show="toast.show"
      :type="toast.type"
      :message="toast.message"
      @close="toast.show = false"
    />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuthStore } from '../../../stores/auth.store.js';
import { useUserStore } from '../../../stores/user.store.js';
import ToastNotification from '../ToastNotification.vue';
import LanguageSelector from './LanguageSelector.vue';
import ThemeToggle from './ThemeToggle.vue';

const { t } = useI18n();
const authStore = useAuthStore();
const userStore = useUserStore();

const apiBaseUrl = (import.meta.env.VITE_API_URL || 'http://localhost:5000').replace(/\/+$/, '');

function getAvatarUrl(url) {
  if (!url) return '';
  if (url.startsWith('http')) return url;
  // Remove /api prefix from base URL for static file serving
  const baseUrl = apiBaseUrl.replace(/\/api$/, '');
  return `${baseUrl}${url.startsWith('/') ? url : '/' + url}`;
}

const emit = defineEmits(['close']);

const formData = reactive({
  nickname: '',
  biography: '',
  avatar_url: ''
});

const passwordData = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const toast = reactive({
  show: false,
  type: 'success',
  message: ''
});

const performanceMode = ref(localStorage.getItem('performanceMode') !== 'false');

onMounted(() => {
  if (authStore.user) {
    formData.nickname = authStore.user.nickname || '';
    formData.biography = authStore.user.biography || '';
    formData.avatar_url = authStore.user.avatar_url || '';
  }
  
  // Apply performance mode on mount
  applyPerformanceMode();
});

function closeModal() {
  emit('close');
}

async function handleAvatarUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  const result = await userStore.uploadAvatar(file);
  
  if (result.success) {
    authStore.user = result.user;
    localStorage.setItem('user', JSON.stringify(result.user));
    
    formData.avatar_url = result.avatar_url;
    toast.show = true;
    toast.type = 'success';
    toast.message = t('profile.avatarUploadSuccess');
  } else {
    toast.show = true;
    toast.type = 'error';
    toast.message = result.error;
  }
}

async function removeAvatar() {
  const result = await userStore.removeAvatar();
  
  if (result.success) {
    authStore.user = result.user;
    localStorage.setItem('user', JSON.stringify(result.user));
    
    formData.avatar_url = '';
    toast.show = true;
    toast.type = 'success';
    toast.message = t('profile.avatarRemoveSuccess');
  } else {
    toast.show = true;
    toast.type = 'error';
    toast.message = result.error;
  }
}

async function saveProfile() {
  const result = await userStore.updateProfile({
    nickname: formData.nickname || null,
    biography: formData.biography || null,
    avatar_url: formData.avatar_url || null
  });

  if (result.success) {
    authStore.user = result.user;
    localStorage.setItem('user', JSON.stringify(result.user));

    toast.show = true;
    toast.type = 'success';
    toast.message = t('profile.saveSuccess');
  } else {
    toast.show = true;
    toast.type = 'error';
    toast.message = result.error;
  }
}

async function updatePassword() {
  if (!passwordData.currentPassword || !passwordData.newPassword) {
    toast.show = true;
    toast.type = 'error';
    toast.message = t('profile.passwordRequired');
    return;
  }

  if (passwordData.newPassword !== passwordData.confirmPassword) {
    toast.show = true;
    toast.type = 'error';
    toast.message = t('profile.passwordMismatch');
    return;
  }

  if (passwordData.newPassword.length < 6) {
    toast.show = true;
    toast.type = 'error';
    toast.message = t('profile.passwordTooShort');
    return;
  }

  const result = await userStore.updatePassword(
    passwordData.currentPassword,
    passwordData.newPassword
  );

  if (result.success) {
    toast.show = true;
    toast.type = 'success';
    toast.message = t('profile.passwordUpdateSuccess');
    
    passwordData.currentPassword = '';
    passwordData.newPassword = '';
    passwordData.confirmPassword = '';
  } else {
    toast.show = true;
    toast.type = 'error';
    toast.message = result.error;
  }
}

function handlePerformanceModeToggle() {
  localStorage.setItem('performanceMode', performanceMode.value.toString());
  applyPerformanceMode();
}

function applyPerformanceMode() {
  if (performanceMode.value) {
    document.body.classList.add('performance-mode');
  } else {
    document.body.classList.remove('performance-mode');
  }
}
</script>
