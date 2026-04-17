<template>
  <div v-if="show" class="modal" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>{{ t('campaign.inviteUsers') }}</h3>
        <button @click="$emit('close')" class="close-btn">×</button>
      </div>
      
      <div class="modal-body">
        <div v-if="loading" class="loading">{{ t('common.loading') }}</div>
        
        <div v-else-if="availableUsers.length === 0" class="empty-state">
          {{ t('campaign.noUsersAvailable') }}
        </div>
        
        <div v-else class="users-list">
          <p class="instruction">{{ t('campaign.selectUsers') }}</p>
          <div 
            v-for="user in availableUsers" 
            :key="user.id" 
            class="user-item"
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
      
      <div class="modal-footer">
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
import { ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useInvitesStore } from '../stores/invites'

const props = defineProps({
  show: Boolean,
  campaignId: Number
})

const emit = defineEmits(['close', 'success'])

const { t } = useI18n()
const invitesStore = useInvitesStore()

const availableUsers = ref([])
const selectedUsers = ref([])
const loading = ref(false)
const sending = ref(false)

watch(() => props.show, async (newValue) => {
  if (newValue && props.campaignId) {
    await loadAvailableUsers()
  } else {
    selectedUsers.value = []
  }
})

async function loadAvailableUsers() {
  loading.value = true
  const result = await invitesStore.getAvailableUsers(props.campaignId)
  if (result.success) {
    availableUsers.value = result.users
  }
  loading.value = false
}

function toggleUser(userId) {
  const index = selectedUsers.value.indexOf(userId)
  if (index > -1) {
    selectedUsers.value.splice(index, 1)
  } else {
    selectedUsers.value.push(userId)
  }
}

async function handleSendInvites() {
  if (selectedUsers.value.length === 0) return
  
  sending.value = true
  const result = await invitesStore.inviteUsers(props.campaignId, selectedUsers.value)
  sending.value = false
  
  if (result.success) {
    emit('success')
    emit('close')
    selectedUsers.value = []
  }
}
</script>

<style scoped>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.close-btn {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.close-btn:hover {
  background-color: rgba(0, 0, 0, 0.1);
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.loading, .empty-state {
  text-align: center;
  padding: 2rem;
  color: var(--text-secondary);
}

.instruction {
  margin-bottom: 1rem;
  color: var(--text-secondary);
  font-size: 0.9rem;
}

.users-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.user-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-item:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.user-item.selected {
  background-color: rgba(76, 175, 80, 0.1);
  border-color: #4CAF50;
}

.user-item input[type="checkbox"] {
  cursor: pointer;
  width: 18px;
  height: 18px;
}

.user-info {
  flex: 1;
}

.username {
  font-weight: 500;
  margin-bottom: 0.25rem;
}

.email {
  font-size: 0.85rem;
  color: var(--text-secondary);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.5rem;
  border-top: 1px solid var(--border-color);
}

.modal-footer button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.modal-footer button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.modal-footer .primary {
  background-color: #4CAF50;
  color: white;
}

.modal-footer .primary:hover:not(:disabled) {
  background-color: #45a049;
}

.modal-footer .secondary {
  background-color: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.modal-footer .secondary:hover {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>
