from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from app import db
from app.models import Post, Campaign, Image
from app.auth import token_required
from app.mock_data import MockDataProvider
import os
import uuid

bp = Blueprint('posts', __name__, url_prefix='/api')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/campaigns/<int:campaign_id>/posts', methods=['GET'])
@token_required
def get_posts(current_user, campaign_id):
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    sort_by = request.args.get('sort', 'created')
    
    if current_app.config['MOCK_DATA']:
        user_id = current_user if isinstance(current_user, int) else current_user.id
        campaign = MockDataProvider.get_campaign(campaign_id)
        
        if not campaign or campaign['owner_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        result = MockDataProvider.get_posts(campaign_id, page, per_page, sort_by)
        return jsonify(result), 200
    
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    query = Post.query.filter_by(campaign_id=campaign_id)
    
    if sort_by == 'updated':
        query = query.order_by(Post.updated_at.asc())
    else:
        query = query.order_by(Post.created_at.asc())
    
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
    
    campaign = Campaign.query.get_or_404(data['campaign_id'])
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    post = Post(
        campaign_id=data['campaign_id'],
        author_id=current_user.id,
        title=data['title'],
        content=data['content']
    )
    
    db.session.add(post)
    db.session.commit()
    
    return jsonify(post.to_dict()), 201

@bp.route('/posts/<int:post_id>', methods=['GET'])
@token_required
def get_post(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(post.to_dict()), 200

@bp.route('/posts/<int:post_id>', methods=['PUT'])
@token_required
def update_post(current_user, post_id):
    post = Post.query.get_or_404(post_id)
    campaign = Campaign.query.get(post.campaign_id)
    
    if campaign.owner_id != current_user.id:
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
    
    if campaign.owner_id != current_user.id:
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
    
    if campaign.owner_id != current_user.id:
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
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
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
