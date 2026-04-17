<template>
  <div class="toast-container">
    <transition-group name="toast">
      <div 
        v-for="toast in invitesStore.toastQueue" 
        :key="toast.id" 
        class="toast"
        @click="invitesStore.removeToast(toast.id)"
      >
        <div class="toast-icon">🔔</div>
        <div class="toast-content">
          <div class="toast-title">{{ t('invite.newInvite') }}</div>
          <div class="toast-message">
            {{ t('invite.inviteMessage', { inviter: toast.inviter, campaign: toast.campaign }) }}
          </div>
        </div>
        <button @click.stop="invitesStore.removeToast(toast.id)" class="toast-close">×</button>
      </div>
    </transition-group>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { useInvitesStore } from '../stores/invites'

const { t } = useI18n()
const invitesStore = useInvitesStore()
</script>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast {
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 1rem;
  min-width: 300px;
  max-width: 400px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  pointer-events: all;
  transition: all 0.3s ease;
}

.toast:hover {
  transform: translateX(-5px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.toast-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: bold;
  margin-bottom: 0.25rem;
  color: var(--text-primary);
}

.toast-message {
  font-size: 0.9rem;
  color: var(--text-secondary);
}

.toast-close {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  flex-shrink: 0;
}

.toast-close:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
