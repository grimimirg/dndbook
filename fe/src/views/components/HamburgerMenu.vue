<template>
  <div>
    <button
        @click="toggleMenu"
        class="hamburger-btn"
        :class="{ 'active': isOpen }"
        aria-label="Menu"
    >
      <span></span>
      <span></span>
      <span></span>
    </button>

    <Teleport to="body">
      <Transition name="menu-overlay">
        <div v-if="isOpen" class="menu-overlay" @click="closeMenu"></div>
      </Transition>

      <Transition name="menu-slide">
        <div v-if="isOpen" class="hamburger-menu">
          <div class="menu-header">
            <h2>{{ t('app.menu') }}</h2>
            <button @click="closeMenu" class="close-menu-btn">✕</button>
          </div>

          <div class="menu-content">
            <div class="menu-section">
              <CampaignDescriptionPanel/>
            </div>

            <div class="menu-section">
              <CampaignCharactersPanel v-if="campaignsStore.currentCampaign"/>
            </div>

            <div class="menu-section">
              <CampaignPlayersPanel v-if="campaignsStore.currentCampaign" ref="playersPanel"/>
            </div>

            <div class="menu-section menu-controls">
              <h3>{{ t('app.settings') }}</h3>
              <div class="control-group">
                <button @click="handleLogout" class="logout-btn primary">
                  {{ t('auth.logout') }}
                </button>
              </div>
              <div class="control-group">
                <label>{{ t('app.language') }}</label>
                <LanguageSelector/>
              </div>
              <div class="control-group">
                <label>{{ t('app.theme') }}</label>
                <ThemeToggle/>
              </div>
            </div>

          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import {ref} from 'vue';
import {useRouter} from 'vue-router';
import {useI18n} from 'vue-i18n';
import {useAuthStore} from '../../stores/auth.store.js';
import {useCampaignsStore} from '../../stores/campaigns.store.js';
import CampaignDescriptionPanel from './CampaignDescriptionPanel.vue';
import CampaignCharactersPanel from './characters/CampaignCharactersPanel.vue';
import CampaignPlayersPanel from './CampaignPlayersPanel.vue';
import LanguageSelector from './LanguageSelector.vue';
import ThemeToggle from './ThemeToggle.vue';

const router = useRouter();
const {t} = useI18n();
const authStore = useAuthStore();
const campaignsStore = useCampaignsStore();

const isOpen = ref(false);
const playersPanel = ref(null);

const emit = defineEmits(['invites-sent']);

function toggleMenu() {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    document.body.style.overflow = 'hidden';
  } else {
    document.body.style.overflow = '';
  }
}

function closeMenu() {
  isOpen.value = false;
  document.body.style.overflow = '';
}

function handleLogout() {
  authStore.logout();
  closeMenu();
  router.push('/login');
}

function handleInvitesSent() {
  if (playersPanel.value) {
    playersPanel.value.fetchMembers();
  }
  emit('invites-sent');
}

defineExpose({
  playersPanel
});
</script>
