import { defineStore } from 'pinia';
import { ref } from 'vue';
import api from '../services/api.service.js';
import { useCampaignsStore } from './campaigns.store.js';

export const usePostsStore = defineStore('posts', () => {
  const campaignsStore = useCampaignsStore();
  const posts = ref([]);
  const loading = ref(false);
  const currentPage = ref(1);
  const totalPages = ref(1);
  const hasMore = ref(false);
  const sortBy = ref('custom');
  const sortDirection = ref('asc');
  const postsPerPage = parseInt(import.meta.env.VITE_POSTS_PER_PAGE || '10');

  async function fetchPosts(campaignId, page = 1, append = false) {
    loading.value = true;
    try {
      const response = await api.get(`/campaigns/${campaignId}/posts`, {
        params: { page, per_page: postsPerPage, sort: sortBy.value, order: sortDirection.value }
      });
      
      if (append) {
        posts.value = [...posts.value, ...response.data.posts];
      } else {
        posts.value = response.data.posts;
      }
      
      currentPage.value = response.data.page;
      totalPages.value = response.data.pages;
      hasMore.value = response.data.has_next;
      
      return { success: true };
    } catch (error) {
      console.error('Failed to fetch posts:', error);
      return { success: false };
    } finally {
      loading.value = false;
    }
  }

  async function createPost(campaignId, title, content) {
    try {
      const response = await api.post('/posts', { 
        campaign_id: campaignId, 
        title, 
        content 
      });
      posts.value.unshift(response.data);
      return { success: true, post: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to create post' 
      };
    }
  }

  async function updatePost(postId, data) {
    try {
      const response = await api.put(`/posts/${postId}`, data);
      const index = posts.value.findIndex(p => p.id === postId);
      if (index !== -1) {
        posts.value[index] = response.data;
      }
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to update post' 
      };
    }
  }

  async function deletePost(postId) {
    try {
      await api.delete(`/posts/${postId}`);
      posts.value = posts.value.filter(p => p.id !== postId);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to delete post' 
      };
    }
  }

  async function uploadImage(postId, file) {
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await api.post(`/posts/${postId}/images`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      return { success: true, image: response.data };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to upload image' 
      };
    }
  }

  async function deleteImage(postId, imageId) {
    try {
      await api.delete(`/posts/${postId}/images/${imageId}`);
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to delete image' 
      };
    }
  }

  function setSortBy(sort) {
    if (sort === 'custom') {
      sortBy.value = 'custom';
      sortDirection.value = 'asc';
    } else if (sort === 'updated') {
      sortBy.value = 'updated';
      sortDirection.value = 'desc';
    } else if (sortBy.value === sort) {
      sortDirection.value = sortDirection.value === 'desc' ? 'asc' : 'desc';
    } else {
      sortBy.value = sort;
      sortDirection.value = 'desc';
    }
  }

  function clearPosts() {
    posts.value = [];
    currentPage.value = 1;
    totalPages.value = 1;
    hasMore.value = true;
  }

  function resetSort() {
    sortBy.value = 'custom';
    sortDirection.value = 'asc';
  }

  async function reorderPosts() {
    if (!posts.value || posts.value.length === 0) {
      return { success: false, error: 'No posts to reorder' };
    }

    const postIds = posts.value.map(post => post.id);
    const firstPostId = postIds[0];
    const campaignId = campaignsStore.currentCampaign?.id;

    if (!campaignId) {
      return { success: false, error: 'No current campaign' };
    }

    try {
      const response = await api.put(`/posts/${firstPostId}/reorder`, { post_ids: postIds });
      // Refresh posts to get updated order from server
      await fetchPosts(campaignId);
      return { success: true };
    } catch (error) {
      console.error('Failed to reorder posts:', error);
      // Refresh posts to revert to server state
      await fetchPosts(campaignId);
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to reorder posts'
      };
    }
  }

  async function createComment(postId, content, postTitle, campaignName) {
    try {
      const response = await api.post(`/posts/${postId}/comments`, {
        content,
        post_title: postTitle,
        campaign_name: campaignName
      });
      const post = posts.value.find(p => p.id === postId);
      if (post) {
        if (!post.comments) {
          post.comments = [];
        }
        post.comments.push(response.data);
      }
      return { success: true, comment: response.data };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to create comment'
      };
    }
  }

  async function updateComment(postId, commentId, content) {
    try {
      const response = await api.put(`/posts/${postId}/comments/${commentId}`, { content });
      const post = posts.value.find(p => p.id === postId);
      if (post && post.comments) {
        const index = post.comments.findIndex(c => c.id === commentId);
        if (index !== -1) {
          post.comments[index] = response.data;
        }
      }
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to update comment' 
      };
    }
  }

  async function deleteComment(postId, commentId) {
    try {
      await api.delete(`/posts/${postId}/comments/${commentId}`);
      const post = posts.value.find(p => p.id === postId);
      if (post && post.comments) {
        post.comments = post.comments.filter(c => c.id !== commentId);
      }
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to delete comment' 
      };
    }
  }

  function $reset() {
    posts.value = [];
    loading.value = false;
    currentPage.value = 1;
    totalPages.value = 1;
    hasMore.value = false;
    sortBy.value = 'custom';
    sortDirection.value = 'asc';
  }

  return {
    posts,
    loading,
    currentPage,
    totalPages,
    hasMore,
    sortBy,
    sortDirection,
    fetchPosts,
    createPost,
    updatePost,
    deletePost,
    uploadImage,
    deleteImage,
    createComment,
    updateComment,
    deleteComment,
    setSortBy,
    resetSort,
    clearPosts,
    reorderPosts,
    $reset
  };
});
