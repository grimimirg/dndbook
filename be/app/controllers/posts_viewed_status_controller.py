from flask import Blueprint, request, jsonify

from app.jwt.jwt_utils import token_required
from app.services.posts_viewed_status_service import PostsViewedStatusService

bp = Blueprint('posts_viewed_status', __name__, url_prefix='/api')

@bp.route('/campaigns/<int:campaign_id>/posts/viewed-status', methods=['GET'])
@token_required
def get_campaign_viewed_status(current_user, campaign_id):
    """
    Get viewed status for all posts in a campaign for the current user.
    
    Only campaign members (not owners) can access viewed status.
    Returns a list of post IDs that have been viewed by the current user.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        
    Returns:
        JSON response with:
        - 200: List of viewed post IDs
        - 403: User is not a campaign member or is the owner
        - 404: Campaign not found
    """
    try:
        viewed_post_ids = PostsViewedStatusService.get_campaign_viewed_status(campaign_id, current_user)
        return jsonify({'viewed_post_ids': viewed_post_ids}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403

@bp.route('/posts/<int:post_id>/mark-viewed', methods=['POST'])
@token_required
def mark_post_viewed(current_user, post_id):
    """
    Mark a post as viewed for the current user.
    
    Only campaign members (not owners) can mark posts as viewed.
    Creates or updates an entry in the PostViewedStatus table.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post to mark as viewed
        
    Returns:
        JSON response with:
        - 200: Success message
        - 403: User is not a campaign member or is the owner
        - 404: Post not found
    """
    try:
        marked = PostsViewedStatusService.mark_post_viewed(post_id, current_user)
        if marked:
            return jsonify({'message': 'Post marked as viewed'}), 200
        else:
            return jsonify({'message': 'Post already marked as viewed'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403
