from flask import Blueprint, request, jsonify

from app.jwt.jwt_utils import token_required
from app.services.characters_service import CharactersService

bp = Blueprint('characters', __name__, url_prefix='/api/campaigns/<int:campaign_id>/characters')


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
    try:
        characters = CharactersService.get_characters(campaign_id, current_user)
        return jsonify(characters), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403


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
    name = request.form.get('name')
    race = request.form.get('race')
    character_class = request.form.get('character_class')
    description = request.form.get('description', '')
    image_file = request.files.get('image') if 'image' in request.files else None
    
    try:
        character = CharactersService.create_character(
            campaign_id=campaign_id,
            user=current_user,
            name=name,
            race=race,
            character_class=character_class,
            description=description,
            image_file=image_file
        )
        return jsonify(character.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'required' in str(e) else 403


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
    try:
        character = CharactersService.get_character(campaign_id, character_id, current_user)
        return jsonify(character.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403


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
    name = request.form.get('name')
    race = request.form.get('race')
    character_class = request.form.get('character_class')
    description = request.form.get('description')
    image_file = request.files.get('image') if 'image' in request.files else None
    remove_image = request.form.get('remove_image') == 'true'
    
    try:
        character = CharactersService.update_character(
            campaign_id=campaign_id,
            character_id=character_id,
            user=current_user,
            name=name,
            race=race,
            character_class=character_class,
            description=description,
            image_file=image_file,
            remove_image=remove_image
        )
        return jsonify(character.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403


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
    try:
        CharactersService.delete_character(campaign_id, character_id, current_user)
        return jsonify({'message': 'Character deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403
