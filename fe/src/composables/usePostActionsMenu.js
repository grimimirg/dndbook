import { ref, onMounted, onUnmounted } from 'vue';
import { usePostsStore } from '../stores/posts.store.js';
import { useCampaignsStore } from '../stores/campaigns.store.js';

export function usePostActionsMenu(emit) {
  const openMenuPostId = ref(null);
  const menuPosition = ref({});
  const postsStore = usePostsStore();
  const campaignsStore = useCampaignsStore();
  const showVisibilityConfirm = ref(false);

  function togglePostMenu(postId, event) {
    if (openMenuPostId.value === postId) {
      openMenuPostId.value = null;
      menuPosition.value = {};
    } else {
      openMenuPostId.value = postId;
      const button = event.currentTarget;
      const rect = button.getBoundingClientRect();

      const menuWidth = 150;
      const top = rect.bottom + 8;
      const left = rect.right - menuWidth;

      menuPosition.value = {
        top: `${top}px`,
        left: `${left}px`,
        right: 'auto'
      };
    }
  }

  function handleEditPost() {
    if (!openMenuPostId.value) return;
    const post = postsStore.posts.find(p => p.id === openMenuPostId.value);
    if (post) {
      emit('edit-post', post);
    }
    openMenuPostId.value = null;
    menuPosition.value = {};
  }

  function showToggleVisibilityConfirm() {
    showVisibilityConfirm.value = true;
  }

  async function confirmToggleVisibility() {
    showVisibilityConfirm.value = false;
    await handleToggleVisibility();
  }

  function cancelToggleVisibility() {
    showVisibilityConfirm.value = false;
    openMenuPostId.value = null;
    menuPosition.value = {};
  }

  async function handleToggleVisibility() {
    if (!openMenuPostId.value) return;
    const post = postsStore.posts.find(p => p.id === openMenuPostId.value);
    if (post && campaignsStore.currentCampaign) {
      const newHiddenState = !post.is_hidden;
      console.log('Toggling visibility for post', post.id, 'to', newHiddenState);
      const result = await postsStore.togglePostVisibility(
        campaignsStore.currentCampaign.id,
        post.id,
        newHiddenState
      );
      console.log('Toggle result:', result);
      if (!result.success) {
        alert(result.error || 'Failed to toggle visibility');
      }
    }
    openMenuPostId.value = null;
    menuPosition.value = {};
  }

  function handleClickOutside(event) {
    const postMenuElement = event.target.closest('.post-actions-menu');
    const menuButton = event.target.closest('.menu-toggle-btn');
    if (!postMenuElement && !menuButton && openMenuPostId.value !== null) {
      openMenuPostId.value = null;
      menuPosition.value = {};
    }
  }

  onMounted(() => {
    document.addEventListener('click', handleClickOutside);
  });

  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
  });

  return {
    openMenuPostId,
    menuPosition,
    togglePostMenu,
    handleEditPost,
    handleToggleVisibility,
    showToggleVisibilityConfirm,
    confirmToggleVisibility,
    cancelToggleVisibility,
    showVisibilityConfirm
  };
}
