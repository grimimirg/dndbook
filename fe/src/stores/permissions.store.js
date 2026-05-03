import { defineStore } from 'pinia';
import { useAuthStore } from './auth.store.js';

/**
 * Centralized permission store for handling ownership and access checks.
 *
 * This store provides reusable functions for checking user permissions
 * on various resources (posts, comments, campaigns, etc.).
 *
 * Adding new permission types:
 * To add a new permission type (e.g., campaign-level permissions):
 * 1. Add a new function following the pattern: `can[Action][Resource](resource)`
 * 2. Use authStore.user to get the current user
 * 3. Compare user properties against resource properties
 * 4. Return boolean indicating permission
 *
 * Example for campaign permissions:
 * ```javascript
 * function canEditCampaign(campaign) {
 *   if (!authStore.user || !campaign) return false;
 *   return authStore.user.id === campaign.owner_id;
 * }
 * ```
 */
export const usePermissionsStore = defineStore('permissions', () => {
  const authStore = useAuthStore();

  /**
   * Check if the current user is the owner of a post.
   * 
   * @param {Object} post - The post object to check
   * @param {number} post.author_id - The ID of the post author
   * @returns {boolean} True if current user is the post owner, false otherwise
   */
  function isPostOwner(post) {
    if (!authStore.user || !post) return false;
    return authStore.user.id === post.author_id;
  }

  /**
   * Check if the current user can edit a post.
   * Currently only checks ownership, but can be extended for admin roles.
   * 
   * @param {Object} post - The post object to check
   * @param {number} post.author_id - The ID of the post author
   * @returns {boolean} True if current user can edit the post, false otherwise
   */
  function canEditPost(post) {
    return isPostOwner(post);
  }

  /**
   * Check if the current user can delete a post.
   * Currently only checks ownership, but can be extended for admin roles.
   * 
   * @param {Object} post - The post object to check
   * @param {number} post.author_id - The ID of the post author
   * @returns {boolean} True if current user can delete the post, false otherwise
   */
  function canDeletePost(post) {
    return isPostOwner(post);
  }

  /**
   * Check if the current user is the owner of a comment.
   * 
   * @param {Object} comment - The comment object to check
   * @param {number} comment.author_id - The ID of the comment author
   * @returns {boolean} True if current user is the comment owner, false otherwise
   */
  function isCommentOwner(comment) {
    if (!authStore.user || !comment) return false;
    return authStore.user.id === comment.author_id;
  }

  /**
   * Check if the current user can edit a comment.
   * 
   * @param {Object} comment - The comment object to check
   * @param {number} comment.author_id - The ID of the comment author
   * @returns {boolean} True if current user can edit the comment, false otherwise
   */
  function canEditComment(comment) {
    return isCommentOwner(comment);
  }

  /**
   * Check if the current user can delete a comment.
   * 
   * @param {Object} comment - The comment object to check
   * @param {number} comment.author_id - The ID of the comment author
   * @returns {boolean} True if current user can delete the comment, false otherwise
   */
  function canDeleteComment(comment) {
    return isCommentOwner(comment);
  }

  return {
    isPostOwner,
    canEditPost,
    canDeletePost,
    isCommentOwner,
    canEditComment,
    canDeleteComment
  };
});
