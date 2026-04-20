import os
from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename

from app import db
from app.jwt.jwt_utils import token_required
from app.models import Campaign, Character

bp = Blueprint('characters', __name__, url_prefix='/api/campaigns/<int:campaign_id>/characters')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('', methods=['GET'])
@token_required
def get_characters(current_user, campaign_id):
    """
    Get all characters for a campaign.
    
    User must be either the campaign owner or a member to access.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        
    Returns:
        JSON response with:
        - 200: Array of character objects
        - 403: User is not authorized to access this campaign
        - 404: Campaign not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)
    
    is_member = campaign.members.filter_by(id=current_user.id).first() is not None
    if campaign.owner_id != current_user.id and not is_member:
        return jsonify({'error': 'Unauthorized'}), 403
    
    characters = Character.query.filter_by(campaign_id=campaign_id).order_by(Character.created_at.desc()).all()
    
    return jsonify([character.to_dict() for character in characters]), 200


@bp.route('', methods=['POST'])
@token_required
def create_character(current_user, campaign_id):
    """
    Create a new character for a campaign.
    
    Only the campaign owner can create characters.
    Supports multipart/form-data for image upload.
    
    Expected form data:
        - name (str): Character name (required)
        - race (str): Character race (required)
        - character_class (str): Character class (required)
        - description (str): Character description (optional)
        - image (file): Character portrait image (optional)
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        
    Returns:
        JSON response with:
        - 201: Created character data
        - 400: Missing required fields or invalid file
        - 403: User is not the campaign owner
        - 404: Campaign not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Only campaign owner can create characters'}), 403
    
    name = request.form.get('name')
    race = request.form.get('race')
    character_class = request.form.get('character_class')
    description = request.form.get('description', '')
    
    if not name or not race or not character_class:
        return jsonify({'error': 'Name, race, and class are required'}), 400
    
    image_url = None
    if 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = str(int(os.path.getmtime(__file__) * 1000))
            unique_filename = f"character_{campaign_id}_{timestamp}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            image_url = f"/uploads/{unique_filename}"
    
    character = Character(
        campaign_id=campaign_id,
        name=name,
        race=race,
        character_class=character_class,
        description=description,
        image_url=image_url
    )
    
    db.session.add(character)
    db.session.commit()
    
    return jsonify(character.to_dict()), 201


@bp.route('/<int:character_id>', methods=['GET'])
@token_required
def get_character(current_user, campaign_id, character_id):
    """
    Get a specific character by ID.
    
    User must be either the campaign owner or a member to access.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        character_id (int): The ID of the character
        
    Returns:
        JSON response with:
        - 200: Character data
        - 403: User is not authorized to access this campaign
        - 404: Campaign or character not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)
    
    is_member = campaign.members.filter_by(id=current_user.id).first() is not None
    if campaign.owner_id != current_user.id and not is_member:
        return jsonify({'error': 'Unauthorized'}), 403
    
    character = Character.query.filter_by(id=character_id, campaign_id=campaign_id).first_or_404()
    
    return jsonify(character.to_dict()), 200


@bp.route('/<int:character_id>', methods=['PUT'])
@token_required
def update_character(current_user, campaign_id, character_id):
    """
    Update a character.
    
    Only the campaign owner can update characters.
    Supports multipart/form-data for image upload.
    
    Expected form data:
        - name (str): Character name (optional)
        - race (str): Character race (optional)
        - character_class (str): Character class (optional)
        - description (str): Character description (optional)
        - image (file): Character portrait image (optional)
        - remove_image (str): Set to 'true' to remove existing image (optional)
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        character_id (int): The ID of the character to update
        
    Returns:
        JSON response with:
        - 200: Updated character data
        - 403: User is not the campaign owner
        - 404: Campaign or character not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Only campaign owner can update characters'}), 403
    
    character = Character.query.filter_by(id=character_id, campaign_id=campaign_id).first_or_404()
    
    if request.form.get('name'):
        character.name = request.form.get('name')
    if request.form.get('race'):
        character.race = request.form.get('race')
    if request.form.get('character_class'):
        character.character_class = request.form.get('character_class')
    if 'description' in request.form:
        character.description = request.form.get('description')
    
    if request.form.get('remove_image') == 'true':
        if character.image_url:
            old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                         character.image_url.replace('/uploads/', ''))
            if os.path.exists(old_image_path):
                os.remove(old_image_path)
        character.image_url = None
    elif 'image' in request.files:
        file = request.files['image']
        if file and file.filename and allowed_file(file.filename):
            if character.image_url:
                old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                             character.image_url.replace('/uploads/', ''))
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            filename = secure_filename(file.filename)
            timestamp = str(int(os.path.getmtime(__file__) * 1000))
            unique_filename = f"character_{campaign_id}_{timestamp}_{filename}"
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            character.image_url = f"/uploads/{unique_filename}"
    
    db.session.commit()
    
    return jsonify(character.to_dict()), 200


@bp.route('/<int:character_id>', methods=['DELETE'])
@token_required
def delete_character(current_user, campaign_id, character_id):
    """
    Delete a character.
    
    Only the campaign owner can delete characters.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        character_id (int): The ID of the character to delete
        
    Returns:
        JSON response with:
        - 200: Success message
        - 403: User is not the campaign owner
        - 404: Campaign or character not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Only campaign owner can delete characters'}), 403
    
    character = Character.query.filter_by(id=character_id, campaign_id=campaign_id).first_or_404()
    
    if character.image_url:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                 character.image_url.replace('/uploads/', ''))
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(character)
    db.session.commit()
    
    return jsonify({'message': 'Character deleted successfully'}), 200
