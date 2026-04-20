<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header flex-between">
        <h3>{{ t('campaign.inviteUsers') }}</h3>
        <button @click="$emit('close')" class="close-btn btn-circle btn-circle-md">×</button>
      </div>
      
      <div class="modal-body">
        <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
        
        <div v-else-if="availableUsers.length === 0" class="empty-state">
          {{ t('campaign.noUsersAvailable') }}
        </div>
        
        <div v-else class="users-list flex-col">
          <p class="instruction">{{ t('campaign.selectUsers') }}</p>
          <div 
            v-for="user in availableUsers" 
            :key="user.id" 
            class="user-item flex-align-center"
            :class="{ selected: selectedUsers.includes(user.id) }"
            @click="toggleUser(user.id)"
          >
            <input 
              type="checkbox" 
              :checked="selectedUsers.includes(user.id)"
              @click.stop="toggleUser(user.id)"
            />
            <div class="user-info">
              <div class="username">{{ user.username }}</div>
              <div class="email">{{ user.email }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-footer flex-end">
        <button @click="$emit('close')" class="secondary">{{ t('campaign.cancel') }}</button>
        <button 
          @click="handleSendInvites" 
          class="primary" 
          :disabled="selectedUsers.length === 0 || sending"
        >
          {{ sending ? t('common.loading') : t('campaign.sendInvites') }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useInvitesStore } from '../../../stores/invites.store.js';

const props = defineProps({
  show: Boolean,
  campaignId: Number
});

const emit = defineEmits(['close', 'success']);

const { t } = useI18n();
const invitesStore = useInvitesStore();

const availableUsers = ref([]);
const selectedUsers = ref([]);
const loading = ref(false);
const sending = ref(false);

watch(() => props.show, async (newValue) => {
  if (newValue && props.campaignId) {
    await loadAvailableUsers();
  } else {
    selectedUsers.value = [];
  }
});

async function loadAvailableUsers() {
  loading.value = true;
  const result = await invitesStore.getAvailableUsers(props.campaignId);
  if (result.success) {
    availableUsers.value = result.users;
  }
  loading.value = false;
}

function toggleUser(userId) {
  const index = selectedUsers.value.indexOf(userId);
  if (index > -1) {
    selectedUsers.value.splice(index, 1);
  } else {
    selectedUsers.value.push(userId);
  }
}

async function handleSendInvites() {
  if (selectedUsers.value.length === 0) return;
  
  sending.value = true;
  const result = await invitesStore.inviteUsers(props.campaignId, selectedUsers.value);
  sending.value = false;
  
  if (result.success) {
    emit('success');
    emit('close');
    selectedUsers.value = [];
  }
}
</script>
