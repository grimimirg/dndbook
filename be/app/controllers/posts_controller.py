from flask import Blueprint, request, jsonify

from app.jwt.jwt_utils import token_required
from app.services.posts_service import PostsService

bp = Blueprint('posts', __name__, url_prefix='/api')

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
    per_page = request.args.get('per_page', None, type=int)
    sort_by = request.args.get('sort', 'order')
    order = request.args.get('order', 'asc')
    importance_level = request.args.get('importance_level', type=int)

    try:
        result = PostsService.get_posts(
            campaign_id=campaign_id,
            user=current_user,
            page=page,
            per_page=per_page,
            sort_by=sort_by,
            order=order,
            importance_level=importance_level
        )
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'importance' in str(e) else 403

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

    try:
        post = PostsService.create_post(
            user=current_user,
            campaign_id=data['campaign_id'],
            title=data['title'],
            content=data['content'],
            importance_level=data.get('importance_level', 0)
        )
        return jsonify(post.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'importance' in str(e) else 403

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
    try:
        post = PostsService.get_post(post_id, current_user)
        return jsonify(post.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403

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
    data = request.get_json()

    try:
        post = PostsService.update_post(
            post_id=post_id,
            user=current_user,
            title=data.get('title'),
            content=data.get('content'),
            importance_level=data.get('importance_level')
        )
        return jsonify(post.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'importance' in str(e) else 403

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
    try:
        PostsService.delete_post(post_id, current_user)
        return jsonify({'message': 'Post deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403

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
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    description = request.form.get('description')
    order_index = request.form.get('order_index', type=int)
    
    try:
        image = PostsService.upload_image(
            post_id=post_id,
            user=current_user,
            file=file,
            description=description,
            order_index=order_index
        )
        return jsonify(image.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'file' in str(e) else 403

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
    try:
        PostsService.delete_image(post_id, image_id, current_user)
        return jsonify({'message': 'Image deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403

@bp.route('/posts/<int:post_id>/images/<int:image_id>', methods=['POST'])
@token_required
def update_image(current_user, post_id, image_id):
    """
    Update an image's description and order.

    User must be campaign owner to modify images.

    Expected JSON payload:
        - description (str): Updated image description (optional)
        - order_index (int): Updated order index (optional)

    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post
        image_id (int): The ID of the image to update

    Returns:
        JSON response with:
        - 200: Updated image data
        - 403: User is not authorized to modify this image
        - 404: Post or image not found
    """
    data = request.get_json()
    
    try:
        image = PostsService.update_image(
            post_id=post_id,
            image_id=image_id,
            user=current_user,
            description=data.get('description'),
            order_index=data.get('order_index')
        )
        return jsonify(image.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403

@bp.route('/posts/<int:post_id>/images/reorder', methods=['PUT'])
@token_required
def reorder_images(current_user, post_id):
    """
    Reorder all images for a post.

    User must be campaign owner to reorder images.

    Expected JSON payload:
        - image_orders (array): Array of objects with image_id and order_index

    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of the post

    Returns:
        JSON response with:
        - 200: Success message
        - 403: User is not authorized to reorder images
        - 404: Post not found
        - 400: Invalid payload
    """
    data = request.get_json()
    
    try:
        PostsService.reorder_images(post_id, current_user, data.get('image_orders', []))
        return jsonify({'message': 'Images reordered successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'image_orders' in str(e) else 403

@bp.route('/posts/<int:post_id>/comments', methods=['POST'])
@token_required
def create_comment(current_user, post_id):
    """
    Create a comment on a post.

    User must have access to the campaign to comment.

    Expected JSON payload:
        - content (str): Comment content (required)
        - post_title (str): Post title (optional, for notification optimization)
        - campaign_name (str): Campaign name (optional, for notification optimization)

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
    data = request.get_json()

    if not data or not data.get('content'):
        return jsonify({'error': 'Missing content'}), 400

    try:
        comment = PostsService.create_comment(
            post_id=post_id,
            user=current_user,
            content=data['content'],
            post_title=data.get('post_title'),
            campaign_name=data.get('campaign_name')
        )
        return jsonify(comment.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 403

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
    data = request.get_json()

    if not data or not data.get('content'):
        return jsonify({'error': 'Missing content'}), 400

    try:
        comment = PostsService.update_comment(post_id, comment_id, current_user, data['content'])
        return jsonify(comment.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403

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
    try:
        PostsService.delete_comment(post_id, comment_id, current_user)
        return jsonify({'message': 'Comment deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403

@bp.route('/posts/<int:post_id>/reorder', methods=['PUT'])
@token_required
def reorder_posts(current_user, post_id):
    """
    Reorder posts within a campaign.

    Accepts an array of post IDs in the new order and updates the order field
    for each post based on its position in the array.

    User must be the campaign owner to reorder posts.

    Expected JSON payload:
        - post_ids (array): Array of post IDs in the desired order

    Args:
        current_user: The authenticated user (injected by token_required decorator)
        post_id (int): The ID of a post in the campaign (used to identify the campaign)

    Returns:
        JSON response with:
        - 200: Success message
        - 400: Missing post_ids array
        - 403: User is not authorized to reorder posts in this campaign
        - 404: Post not found
    """
    data = request.get_json()

    if not data or not data.get('post_ids') or not isinstance(data['post_ids'], list):
        return jsonify({'error': 'Missing or invalid post_ids array'}), 400

    try:
        PostsService.reorder_posts(post_id, current_user, data['post_ids'])
        return jsonify({'message': 'Posts reordered successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'Post' in str(e) else 403
