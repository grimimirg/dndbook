from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
import uuid

from app.jwt.jwt_utils import token_required
from app.services.user_service import UserService

bp = Blueprint('user', __name__, url_prefix='/api/user')


@bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    """
    Update user profile information.

    Expected JSON payload:
        - nickname (str, optional): New nickname
        - biography (str, optional): New biography
        - avatar_url (str, optional): New avatar URL

    Returns:
        JSON response with:
        - 200: Success with updated user data
        - 400: Validation error
    """
    data = request.get_json()

    if not data:
        return jsonify({'error': 'No data provided'}), 400

    try:
        kwargs = {
            'user_id': current_user.id,
            'nickname': data.get('nickname'),
            'biography': data.get('biography'),
        }
        if 'avatar_url' in data:
            kwargs['avatar_url'] = data['avatar_url']
        user = UserService.update_profile(**kwargs)
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


@bp.route('/password', methods=['PUT'])
@token_required
def update_password(current_user):
    """
    Update user password.

    Expected JSON payload:
        - current_password (str): Current password for verification
        - new_password (str): New password

    Returns:
        JSON response with:
        - 200: Success
        - 400: Validation error
        - 401: Current password incorrect
    """
    data = request.get_json()

    if not data or not data.get('current_password') or not data.get('new_password'):
        return jsonify({'error': 'Missing required fields'}), 400

    try:
        UserService.update_password(
            user_id=current_user.id,
            current_password=data['current_password'],
            new_password=data['new_password']
        )
        return jsonify({'message': 'Password updated successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401


@bp.route('/avatar', methods=['POST'])
@token_required
def upload_avatar(current_user):
    """
    Upload user avatar.

    Expected form data:
        - avatar (file): Image file

    Returns:
        JSON response with:
        - 200: Success with avatar URL
        - 400: No file provided or invalid file type
    """
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['avatar']

    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''

    if file_ext not in allowed_extensions:
        return jsonify({'error': 'Invalid file type. Allowed types: png, jpg, jpeg, gif, webp'}), 400

    # Generate unique filename
    filename = secure_filename(file.filename)
    unique_filename = f"{uuid.uuid4()}_{filename}"
    upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'avatars')
    os.makedirs(upload_path, exist_ok=True)
    file_path = os.path.join(upload_path, unique_filename)
    file.save(file_path)

    # Generate URL
    avatar_url = f"/uploads/avatars/{unique_filename}"

    # Update user avatar
    try:
        user = UserService.update_profile(
            user_id=current_user.id,
            avatar_url=avatar_url
        )
        return jsonify({
            'message': 'Avatar uploaded successfully',
            'avatar_url': avatar_url,
            'user': user.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
