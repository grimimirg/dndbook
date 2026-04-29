from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Post, Campaign, Image, Comment, Notification
from app.jwt.jwt_utils import token_required
from app.controllers.mock_data_controller import MockDataProvider
from app.events.socketio_events import send_notification
import os
import uuid

bp = Blueprint('posts', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """
    Check if a filename has an allowed extension.
    
    Args:
        filename (str): The filename to check
        
    Returns:
        bool: True if the file extension is allowed, False otherwise
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def can_access_campaign(campaign, user):
    """
    Check if user can access campaign (owner or member).
    
    Args:
        campaign: The campaign object to check access for
        user: The user object to verify
        
    Returns:
        bool: True if user is owner or member, False otherwise
    """
    if campaign.owner_id == user.id:
        return True
    is_member = campaign.members.filter_by(id=user.id).first() is not None
    return is_member

def create_notification_entries(user_id, campaign_id, notification_type, title, message, related_post_id=None):
    """
    Create notification entries for all campaign members (excluding owner).
    
    Args:
        user_id (int): The ID of the user who triggered the notification (will be excluded)
        campaign_id (int): The ID of the campaign
        notification_type (str): Type of notification ('post_created', 'post_edited', 'invite')
        title (str): Notification title
        message (str): Notification message
        related_post_id (int, optional): Related post ID for post notifications
    """
    campaign = Campaign.query.get(campaign_id)
    if not campaign:
        return
    
    # Query campaign members excluding the owner
    members = campaign.members.filter(Campaign.id != campaign.owner_id).all()
    
    # Create notification entries for all members
    for member in members:
        # Skip the user who made the change
        if member.id == user_id:
            continue
        
        notification = Notification(
            user_id=member.id,
            campaign_id=campaign_id,
            notification_type=notification_type,
            title=title,
            message=message,
            related_post_id=related_post_id
        )
        db.session.add(notification)
        
        # Send WebSocket notification to the member
        send_notification(member.id)
    
    db.session.commit()

@bp.route('/campaigns/<int:campaign_id>/posts', methods=['GET'])
@token_required
def get_posts(current_user, campaign_id):
    """
    Get paginated posts for a campaign.
    
    Supports sorting by created or updated date, and ascending or descending order.
    User must be campaign owner or member to access.
    
    Query parameters:
        - page (int): Page number (default: 1)
        - per_page (int): Items per page (default: from config)
        - sort (str): Sort field - 'created' or 'updated' (default: 'updated')
        - order (str): Sort order - 'asc' or 'desc' (default: 'desc')
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        
    Returns:
        JSON response with:
        - 200: Paginated posts with metadata (total, page, pages, has_next, has_prev)
        - 403: User is not authorized to access this campaign
        - 404: Campaign not found
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', current_app.config['POSTS_PER_PAGE'], type=int)
    sort_by = request.args.get('sort', 'updated')
    order = request.args.get('order', 'desc')
    
    if current_app.config['MOCK_DATA']:
        user_id = current_user if isinstance(current_user, int) else current_user.id
        campaign = MockDataProvider.get_campaign(campaign_id)
        
        if not campaign or campaign['owner_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        result = MockDataProvider.get_posts(campaign_id, page, per_page, sort_by, order)
        return jsonify(result), 200
    
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if not can_access_campaign(campaign, current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    query = Post.query.filter_by(campaign_id=campaign_id)
    
    # Determina il campo di ordinamento
    order_field = Post.updated_at if sort_by == 'updated' else Post.created_at
    
    # Applica la direzione di ordinamento
    if order == 'asc':
        query = query.order_by(order_field.asc())
    else:
        query = query.order_by(order_field.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'posts': [post.to_dict() for post in pagination.items],
        'total': pagination.total,
        'page': pagination.page,
        'pages': pagination.pages,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    }), 200

@bp.route('/posts', methods=['POST'])
@token_required
def create_post(current_user):
    """
    Create a new post in a campaign.
    
    User must be campaign owner or member to create posts.
    
    Expected JSON payload:
        - campaign_id (int): The campaign ID (required)
        - title (str): Post title (required)
        - content (str): Post content (required)
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        
    Returns:
        JSON response with:
        - 201: Created post data
        - 400: Missing required fields
        - 403: User is not authorized to post in this campaign
        - 404: Campaign not found
    """
    data = request.get_json()
    
    if not data or not data.get('campaign_id') or not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Missing required fields'}), 400
    
    if current_app.config['MOCK_DATA']:
        user_id = current_user if isinstance(current_user, int) else current_user.id
        campaign = MockDataProvider.get_campaign(data['campaign_id'])
        
        if not campaign or campaign['owner_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        new_post = MockDataProvider.create_post(
            data['campaign_id'],
            user_id,
            data['title'],
            data['content']
        )
        return jsonify(new_post), 201
    
    campaign = Campaign.query.get_or_404(data['campaign_id'])
    
    if not can_access_campaign(campaign, current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    post = Post(
        campaign_id=data['campaign_id'],
        author_id=current_user.id,
        title=data['title'],
        content=data['content']
    )
    
    db.session.add(post)
    db.session.commit()
    db.session.refresh(post)
    
    # Create notifications for campaign members (excluding owner and author)
    create_notification_entries(
        user_id=current_user.id,
        campaign_id=data['campaign_id'],
        notification_type='post_created',
        title=f'New post: {data["title"]}',
        message=f'A new post "{data["title"]}" was created in the campaign.',
        related_post_id=post.id
    )
    
    return jsonify(post.to_dict()), 201

@bp.route('/posts/<int:post_id>', methods=['GET'])
@token_required
def get_post(current_user, post_id):
    """
    Get a specific post by ID.
    
    User must have access to the campaign to view the post.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post to retrieve
        
    Returns:
        JSON response with:
        - 200: Post data
        - 403: User is not authorized to access this post
        - 404: Post not found
    """
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if not can_access_campaign(campaign, current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(post.to_dict()), 200

@bp.route('/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(current_user, post_id):
    """
    Update a post.
    
    User must have access to the campaign to update posts.
    
    Expected JSON payload:
        - title (str): Updated post title (optional)
        - content (str): Updated post content (optional)
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post to update
        
    Returns:
        JSON response with:
        - 200: Updated post data
        - 403: User is not authorized to update this post
        - 404: Post not found
    """
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if not can_access_campaign(campaign, current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if data.get('title'):
        post.title = data['title']
    if data.get('content'):
        post.content = data['content']
    
    db.session.commit()
    
    # Create notifications for campaign members (excluding owner and author)
    create_notification_entries(
        user_id=current_user.id,
        campaign_id=post.campaign_id,
        notification_type='post_edited',
        title=f'Post updated: {post.title}',
        message=f'The post "{post.title}" was edited in the campaign.',
        related_post_id=post.id
    )
    
    return jsonify(post.to_dict()), 200

@bp.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
    """
    Delete a post and all associated images.
    
    User must have access to the campaign to delete posts.
    Deletes all image files from disk and database records.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post to delete
        
    Returns:
        JSON response with:
        - 200: Success message
        - 403: User is not authorized to delete this post
        - 404: Post not found
    """
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if not can_access_campaign(campaign, current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    for image in post.images:
        try:
            os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.file_path))
        except:
            pass
    
    db.session.delete(post)
    db.session.commit()
    
    return jsonify({'message': 'Post deleted successfully'}), 200

@bp.route('/posts/<int:post_id>/images', methods=['POST'])
@token_required
def upload_image(current_user, post_id):
    """
    Upload an image to a post.
    
    User must have access to the campaign to upload images.
    Accepts multipart/form-data with a 'file' field.
    Allowed extensions: png, jpg, jpeg, gif, webp.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post to add the image to
        
    Returns:
        JSON response with:
        - 201: Created image data
        - 400: No file provided, no file selected, or file type not allowed
        - 403: User is not authorized to upload to this post
        - 404: Post not found
    """
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if not can_access_campaign(campaign, current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed'}), 400
    
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    
    # Ensure upload directory exists
    upload_folder = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_folder, mode=0o755, exist_ok=True)
    
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)
    
    order_index = len(post.images)
    
    image = Image(
        post_id=post_id,
        file_path=unique_filename,
        order_index=order_index
    )
    
    db.session.add(image)
    db.session.commit()
    
    return jsonify(image.to_dict()), 201

@bp.route('/posts/<int:post_id>/images/<int:image_id>', methods=['DELETE'])
@token_required
def delete_image(current_user, post_id, image_id):
    """
    Delete an image from a post.
    
    User must have access to the campaign to delete images.
    Removes the image file from disk and database record.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post
        image_id (int): The ID of the image to delete
        
    Returns:
        JSON response with:
        - 200: Success message
        - 403: User is not authorized to delete this image
        - 404: Post or image not found
    """
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if not can_access_campaign(campaign, current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    image = Image.query.filter_by(id=image_id, post_id=post_id).first_or_404()
    
    try:
        os.remove(os.path.join(current_app.config['UPLOAD_FOLDER'], image.file_path))
    except:
        pass
    
    db.session.delete(image)
    db.session.commit()
    
    return jsonify({'message': 'Image deleted successfully'}), 200

@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def create_comment(current_user, post_id):
    """
    Create a comment on a post.
    
    User must have access to the campaign to comment.
    
    Expected JSON payload:
        - content (str): Comment content (required)
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post to comment on
        
    Returns:
        JSON response with:
        - 201: Created comment data
        - 400: Missing content
        - 403: User is not authorized to comment on this post
        - 404: Post not found
    """
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if not can_access_campaign(campaign, current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': 'Missing content'}), 400
    
    comment = Comment(
        post_id=post_id,
        author_id=current_user.id,
        content=data['content']
    )
    
    db.session.add(comment)
    db.session.commit()
    db.session.refresh(comment)
    
    return jsonify(comment.to_dict()), 201

@bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['PUT'])
@token_required
def update_comment(current_user, post_id, comment_id):
    """
    Update a comment.
    
    Only the comment author can update their comment.
    
    Expected JSON payload:
        - content (str): Updated comment content (required)
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post
        comment_id (int): The ID of the comment to update
        
    Returns:
        JSON response with:
        - 200: Updated comment data
        - 400: Missing content
        - 403: User is not the comment author
        - 404: Post or comment not found
    """
    comment = Comment.query.filter_by(id=comment_id, post_id=post_id).first_or_404()
    
    if comment.author_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if not data or not data.get('content'):
        return jsonify({'error': 'Missing content'}), 400
    
    comment.content = data['content']
    db.session.commit()
    
    return jsonify(comment.to_dict()), 200

@bp.route('/posts/<int:post_id>/comments/<int:comment_id>', methods=['DELETE'])
@token_required
def delete_comment(current_user, post_id, comment_id):
    """
    Delete a comment.
    
    Only the comment author can delete their comment.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post
        comment_id (int): The ID of the comment to delete
        
    Returns:
        JSON response with:
        - 200: Success message
        - 403: User is not the comment author
        - 404: Post or comment not found
    """
    comment = Comment.query.filter_by(id=comment_id, post_id=post_id).first_or_404()
    
    if comment.author_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment deleted successfully'}), 200
