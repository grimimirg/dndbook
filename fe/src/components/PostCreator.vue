<template>
  <div class="post-creator card">
    <form @submit.prevent="handleCreatePost">
      <div class="form-group">
        <input v-model="title" :placeholder="$t('post.title')" required />
      </div>
      <div class="form-group">
        <textarea 
          v-model="content" 
          :placeholder="$t('post.content')" 
          rows="4"
          required
        ></textarea>
      </div>
      <div class="actions">
        <button type="submit" class="primary" :disabled="loading">
          {{ loading ? $t('post.creating') : $t('post.createPost') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useCampaignsStore } from '../stores/campaigns'
import { usePostsStore } from '../stores/posts'

const campaignsStore = useCampaignsStore()
const postsStore = usePostsStore()

const title = ref('')
const content = ref('')
const loading = ref(false)

async function handleCreatePost() {
  if (!campaignsStore.currentCampaign) return
  
  loading.value = true
  
  const result = await postsStore.createPost(
    campaignsStore.currentCampaign.id,
    title.value,
    content.value
  )
  
  loading.value = false
  
  if (result.success) {
    title.value = ''
    content.value = ''
  }
}
</script>

<style scoped>
.post-creator {
  margin-bottom: 16px;
}

.form-group {
  margin-bottom: 12px;
}

.actions {
  display: flex;
  justify-content: flex-end;
}
</style>
