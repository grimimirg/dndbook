import { ref, onMounted, onUnmounted } from 'vue';
import { usePostsStore } from '../stores/posts.store.js';

export function usePostActionsMenu(emit) {
  const openMenuPostId = ref(null);
  const menuPosition = ref({});
  const postsStore = usePostsStore();

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
    handleEditPost
  };
}
