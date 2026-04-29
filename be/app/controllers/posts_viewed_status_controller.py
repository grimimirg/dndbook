from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Post, Campaign, PostViewedStatus
from app.jwt.jwt_utils import token_required

bp = Blueprint('posts_viewed_status', __name__, url_prefix='/api')

def is_campaign_member(campaign, user):
    """
    Check if user is a campaign member (not owner).
    
    Args:
        campaign: The campaign object to check access for
        user: The user object to verify
        
    Returns:
        bool: True if user is a member (not owner), False otherwise
    """
    if campaign.owner_id == user.id:
        return False
    is_member = campaign.members.filter_by(id=user.id).first() is not None
    return is_member

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
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if not is_campaign_member(campaign, current_user):
        return jsonify({'error': 'Unauthorized - viewed status only available to campaign members'}), 403
    
    # Query PostViewedStatus table for user's viewed posts in this campaign
    viewed_posts = db.session.query(PostViewedStatus.c.post_id)\
        .filter(PostViewedStatus.c.user_id == current_user.id)\
        .join(Post, PostViewedStatus.c.post_id == Post.id)\
        .filter(Post.campaign_id == campaign_id)\
        .all()
    
    viewed_post_ids = [post_id for (post_id,) in viewed_posts]
    
    return jsonify({'viewed_post_ids': viewed_post_ids}), 200

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
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if not is_campaign_member(campaign, current_user):
        return jsonify({'error': 'Unauthorized - only campaign members can mark posts as viewed'}), 403
    
    # Check if entry already exists
    existing = db.session.query(PostViewedStatus)\
        .filter(PostViewedStatus.c.user_id == current_user.id)\
        .filter(PostViewedStatus.c.post_id == post_id)\
        .first()
    
    if existing:
        # Entry already exists, post already viewed
        return jsonify({'message': 'Post already marked as viewed'}), 200
    
    # Create new entry
    db.session.execute(
        PostViewedStatus.insert().values(
            user_id=current_user.id,
            post_id=post_id
        )
    )
    db.session.commit()
    
    return jsonify({'message': 'Post marked as viewed'}), 200
