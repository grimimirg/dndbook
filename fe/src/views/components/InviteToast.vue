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
import { useI18n } from 'vue-i18n';
import { useInvitesStore } from '../../stores/invites.store.js';

const { t } = useI18n();
const invitesStore = useInvitesStore();
</script>
