import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '../services/api'

export const usePostsStore = defineStore('posts', () => {
  const posts = ref([])
  const loading = ref(false)
  const currentPage = ref(1)
  const totalPages = ref(1)
  const hasMore = ref(false)
  const sortBy = ref('updated')
  const sortDirection = ref('desc')
  const postsPerPage = parseInt(import.meta.env.VITE_POSTS_PER_PAGE || '10')

  async function fetchPosts(campaignId, page = 1, append = false) {
    loading.value = true
    try {
      const response = await api.get(`/api/campaigns/${campaignId}/posts`, {
        params: { page, per_page: postsPerPage, sort: sortBy.value, order: sortDirection.value }
      })
      
      if (append) {
        posts.value = [...posts.value, ...response.data.posts]
      } else {
        posts.value = response.data.posts
      }
      
      currentPage.value = response.data.page
      totalPages.value = response.data.pages
      hasMore.value = response.data.has_next
      
      return { success: true }
    } catch (error) {
      console.error('Failed to fetch posts:', error)
      return { success: false }
    } finally {
      loading.value = false
    }
  }

  async function createPost(campaignId, title, content) {
    try {
      const response = await api.post('/api/posts', { 
        campaign_id: campaignId, 
        title, 
        content 
      })
      posts.value.unshift(response.data)
      return { success: true, post: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to create post' 
      }
    }
  }

  async function updatePost(postId, data) {
    try {
      const response = await api.put(`/api/posts/${postId}`, data)
      const index = posts.value.findIndex(p => p.id === postId)
      if (index !== -1) {
        posts.value[index] = response.data
      }
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to update post' 
      }
    }
  }

  async function deletePost(postId) {
    try {
      await api.delete(`/api/posts/${postId}`)
      posts.value = posts.value.filter(p => p.id !== postId)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to delete post' 
      }
    }
  }

  async function uploadImage(postId, file) {
    try {
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post(`/api/posts/${postId}/images`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      return { success: true, image: response.data }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to upload image' 
      }
    }
  }

  async function deleteImage(postId, imageId) {
    try {
      await api.delete(`/api/posts/${postId}/images/${imageId}`)
      return { success: true }
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.error || 'Failed to delete image' 
      }
    }
  }

  function setSortBy(sort) {
    if (sortBy.value === sort) {
      sortDirection.value = sortDirection.value === 'desc' ? 'asc' : 'desc'
    } else {
      sortBy.value = sort
      sortDirection.value = 'desc'
    }
  }

  function clearPosts() {
    posts.value = []
    currentPage.value = 1
    totalPages.value = 1
    hasMore.value = true
  }

  function resetSort() {
    sortBy.value = 'updated'
    sortDirection.value = 'desc'
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
    setSortBy,
    resetSort,
    clearPosts
  }
})
