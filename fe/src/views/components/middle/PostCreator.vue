<template>
  <div class="post-creator card">
    <form @submit.prevent="handleCreatePost">
      <div class="form-group">
        <input v-model="title" :placeholder="t('post.title')" required />
      </div>
      <div class="form-group">
        <textarea
          ref="contentTextarea"
          v-model="content"
          :placeholder="t('post.content')"
          rows="4"
          required
          @input="handleContentInput"
          @keydown="handleKeydown"
          @click="handleClick"
        ></textarea>
      </div>

      <MentionAutocomplete
        :show="showMentionAutocomplete"
        :query="mentionQuery"
        :campaign-id="campaignsStore.currentCampaign?.id"
        :textarea-ref="contentTextarea"
        @select="handleMentionSelect"
        @close="closeMentionAutocomplete"
        ref="mentionAutocomplete"
      />

      <div class="form-group">
        <label>{{ t('post.importance') }}</label>
        <div class="importance-selector">
          <span
              v-for="i in 10"
              :key="i"
              @click="importanceLevel = i"
              class="importance-mark"
              :class="{ active: i <= importanceLevel }"
          >
            👑
          </span>
        </div>
      </div>

      <div v-if="isOwner" class="form-group">
        <div class="visibility-toggle flex-align-center" @click="isHidden = !isHidden" style="cursor: pointer;">
          <input type="checkbox" v-model="isHidden" class="hidden-checkbox" @click.stop />
          <span class="eye-toggle" :title="t('post.hideFromPlayers')">
            {{ isHidden ? '🔒' : '👁️' }}
          </span>
          <span>{{ t('post.hideFromPlayers') }}</span>
        </div>
      </div>

      <div v-if="selectedImages.length > 0" class="image-previews">
        <div v-for="(image, index) in selectedImages" :key="index" class="image-preview">
          <img :src="image.preview" :alt="`Preview ${index + 1}`" />
          <button @click="moveImageUp(index)" v-if="index > 0" class="move-image btn-circle btn-circle-sm">↑</button>
          <button @click="moveImageDown(index)" v-if="index < selectedImages.length - 1" class="move-image btn-circle btn-circle-sm">↓</button>
          <button @click="removeImage(index)" class="remove-image btn-circle btn-circle-sm">×</button>
          <textarea
            v-model="image.description"
            :placeholder="t('post.imageDescription')"
            class="image-description"
            rows="2"
          ></textarea>
        </div>
      </div>

      <div v-if="selectedImages.length >= 10" class="max-images-warning">
        {{ t('post.maxImagesWarning', { max: 10 }) }}
      </div>

      <div class="actions flex-between">
        <div class="post-upload-group">
          <label class="image-upload-btn flex-align-center">
            <input
              type="file"
              ref="fileInput"
              @change="handleImageSelect"
              accept="image/png,image/jpeg,image/jpg,image/gif,image/webp"
              multiple
              class="hidden-file-input"
            />
            <span class="upload-icon">📷</span>
            <span>{{ t('post.addImages') }}</span>
          </label>
          <div
            class="post-drop-zone"
            :class="{ 'drag-over': isPostDragOver }"
            @dragover.prevent="isPostDragOver = true"
            @dragleave.prevent="isPostDragOver = false"
            @drop.prevent="handlePostDrop"
          >
            {{ t('post.dropHere') }}
          </div>
        </div>
        <button type="submit" class="primary" :disabled="loading">
          {{ loading ? t('post.creating') : t('post.createPost') }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useCampaignsStore } from '../../../stores/campaigns.store.js';
import { usePostsStore } from '../../../stores/posts.store.js';
import { useAuthStore } from '../../../stores/auth.store.js';
import MentionAutocomplete from '../MentionAutocomplete.vue';

const { t } = useI18n();
const campaignsStore = useCampaignsStore();
const postsStore = usePostsStore();
const authStore = useAuthStore();

const title = ref('');
const content = ref('');
const importanceLevel = ref(0);
const isHidden = ref(false);
const loading = ref(false);
const selectedImages = ref([]);
const fileInput = ref(null);
const isPostDragOver = ref(false);
const contentTextarea = ref(null);
const mentionAutocomplete = ref(null);

// Mention autocomplete state
const showMentionAutocomplete = ref(false);
const mentionQuery = ref('');
const mentionStartIndex = ref(0);

const isOwner = computed(() => {
  return campaignsStore.currentCampaign?.owner_id === authStore.user?.id;
});

function handleImageSelect(event) {
  const files = Array.from(event.target.files);

  if (selectedImages.value.length + files.length > 10) {
    alert(t('post.maxImagesWarning', { max: 10 }));
    return;
  }

  files.forEach(file => {
    if (file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        selectedImages.value.push({
          file: file,
          preview: e.target.result,
          description: ''
        });
      };
      reader.readAsDataURL(file);
    }
  });

  if (fileInput.value) {
    fileInput.value.value = '';
  }
}

function handlePostDrop(event) {
  isPostDragOver.value = false;
  const files = Array.from(event.dataTransfer.files).filter(f => f.type.startsWith('image/'));
  if (!files.length) return;
  if (selectedImages.value.length + files.length > 10) {
    alert(t('post.maxImagesWarning', { max: 10 }));
    return;
  }
  files.forEach(file => {
    const reader = new FileReader();
    reader.onload = (e) => {
      selectedImages.value.push({ file, preview: e.target.result, description: '' });
    };
    reader.readAsDataURL(file);
  });
}

function removeImage(index) {
  selectedImages.value.splice(index, 1);
}

function moveImageUp(index) {
  if (index > 0) {
    const temp = selectedImages.value[index];
    selectedImages.value[index] = selectedImages.value[index - 1];
    selectedImages.value[index - 1] = temp;
  }
}

function moveImageDown(index) {
  if (index < selectedImages.value.length - 1) {
    const temp = selectedImages.value[index];
    selectedImages.value[index] = selectedImages.value[index + 1];
    selectedImages.value[index + 1] = temp;
  }
}

function handleContentInput(event) {
  const textarea = event.target;
  const cursorPosition = textarea.selectionStart;
  const textBeforeCursor = content.value.substring(0, cursorPosition);

  // Check if we just typed @
  const lastChar = textBeforeCursor.slice(-1);
  if (lastChar === '@') {
    showMentionAutocomplete.value = true;
    mentionQuery.value = '';
    mentionStartIndex.value = cursorPosition - 1;
  } else if (showMentionAutocomplete.value) {
    // Extract the word after @
    const atIndex = textBeforeCursor.lastIndexOf('@');
    if (atIndex !== -1) {
      const wordAfterAt = textBeforeCursor.substring(atIndex + 1);
      // Check if there's a space after @
      if (wordAfterAt.includes(' ')) {
        closeMentionAutocomplete();
      } else {
        mentionQuery.value = wordAfterAt;
      }
    } else {
      closeMentionAutocomplete();
    }
  }
}

function handleKeydown(event) {
  if (showMentionAutocomplete.value && mentionAutocomplete.value) {
    mentionAutocomplete.value.handleKeydown(event);
  }
}

function handleClick() {
  closeMentionAutocomplete();
}

function handleMentionSelect(character) {
  if (!contentTextarea.value) return;

  const textarea = contentTextarea.value;
  const cursorPosition = textarea.selectionStart;
  const textBeforeMention = content.value.substring(0, mentionStartIndex.value);
  const textAfterCursor = content.value.substring(cursorPosition);

  // Replace @query with @character_name
  content.value = textBeforeMention + `@${character.name}` + textAfterCursor;

  // Set cursor position after the mention
  const newCursorPosition = mentionStartIndex.value + character.name.length + 1;
  textarea.setSelectionRange(newCursorPosition, newCursorPosition);
  textarea.focus();

  closeMentionAutocomplete();
}

function closeMentionAutocomplete() {
  showMentionAutocomplete.value = false;
  mentionQuery.value = '';
}

async function handleCreatePost() {
  if (!campaignsStore.currentCampaign) return;

  loading.value = true;

  const result = await postsStore.createPost(
    campaignsStore.currentCampaign.id,
    title.value,
    content.value,
    importanceLevel.value,
    isHidden.value
  );

  if (result.success && result.post) {
    const postId = result.post.id;

    for (const [index, image] of selectedImages.value.entries()) {
      await postsStore.uploadImage(postId, image.file, image.description, index);
    }

    await postsStore.fetchPosts(campaignsStore.currentCampaign.id);

    title.value = '';
    content.value = '';
    importanceLevel.value = 0;
    isHidden.value = false;
    selectedImages.value = [];
  }

  loading.value = false;
}
</script>
