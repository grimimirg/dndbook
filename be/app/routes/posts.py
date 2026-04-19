from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Post, Campaign, Image, Comment
from app.auth import token_required
from app.mock_data import MockDataProvider
import os
import uuid

bp = Blueprint('posts', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def can_access_campaign(campaign, user):
    """Check if user can access campaign (owner or member)"""
    if campaign.owner_id == user.id:
        return True
    is_member = campaign.members.filter_by(id=user.id).first() is not None
    return is_member

@bp.route('/campaigns/<int:campaign_id>/posts', methods=['GET'])
@token_required
def get_posts(current_user, campaign_id):
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
    
    return jsonify(post.to_dict()), 201

@bp.route('/posts/<int:post_id>', methods=['GET'])
@token_required
def get_post(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if not can_access_campaign(campaign, current_user):
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(post.to_dict()), 200

@bp.route('/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(current_user, post_id):
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
    
    return jsonify(post.to_dict()), 200

@bp.route('/posts/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(current_user, post_id):
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
    comment = Comment.query.filter_by(id=comment_id, post_id=post_id).first_or_404()
    
    if comment.author_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(comment)
    db.session.commit()
    
    return jsonify({'message': 'Comment deleted successfully'}), 200
