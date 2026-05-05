"""Service for character operations."""

import os
from flask import current_app
from werkzeug.utils import secure_filename

from app import db
from app.models import Campaign, Character


class CharactersService:
    """Service for handling character business logic."""

    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

    @staticmethod
    def allowed_file(filename):
        """Check if file extension is allowed."""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in CharactersService.ALLOWED_EXTENSIONS

    @staticmethod
    def get_characters(campaign_id, user):
        """
        Get all characters for a campaign.

        User must be either the campaign owner or a member to access.

        Args:
            campaign_id (int): The ID of the campaign
            user: The user requesting access

        Returns:
            list: Array of character objects

        Raises:
            ValueError: If user is not authorized
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        is_member = campaign.members.filter_by(id=user.id).first() is not None
        if campaign.owner_id != user.id and not is_member:
            raise ValueError('Unauthorized')

        characters = Character.query.filter_by(campaign_id=campaign_id).order_by(Character.created_at.desc()).all()

        return [character.to_dict() for character in characters]

    @staticmethod
    def create_character(campaign_id, user, name, race, character_class, description='', image_file=None):
        """
        Create a new character for a campaign.

        Only the campaign owner can create characters.

        Args:
            campaign_id (int): The ID of the campaign
            user: The user creating the character
            name (str): Character name
            race (str): Character race
            character_class (str): Character class
            description (str): Character description
            image_file: File object for character portrait (optional)

        Returns:
            Character: The created character

        Raises:
            ValueError: If user is not the campaign owner or missing required fields
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if campaign.owner_id != user.id:
            raise ValueError('Only campaign owner can create characters')

        if not name or not race or not character_class:
            raise ValueError('Name, race, and class are required')

        image_url = CharactersService._save_character_image(image_file, campaign_id) if image_file else None

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

        return character

    @staticmethod
    def get_character(campaign_id, character_id, user):
        """
        Get a specific character by ID.

        User must be either the campaign owner or a member to access.

        Args:
            campaign_id (int): The ID of the campaign
            character_id (int): The ID of the character
            user: The user requesting access

        Returns:
            Character: The character object

        Raises:
            ValueError: If user is not authorized
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        is_member = campaign.members.filter_by(id=user.id).first() is not None
        if campaign.owner_id != user.id and not is_member:
            raise ValueError('Unauthorized')

        character = Character.query.filter_by(id=character_id, campaign_id=campaign_id).first_or_404()

        return character

    @staticmethod
    def update_character(campaign_id, character_id, user, name=None, race=None, character_class=None,
                        description=None, image_file=None, remove_image=False):
        """
        Update a character.

        Only the campaign owner can update characters.

        Args:
            campaign_id (int): The ID of the campaign
            character_id (int): The ID of the character
            user: The user requesting the update
            name (str): Updated character name (optional)
            race (str): Updated character race (optional)
            character_class (str): Updated character class (optional)
            description (str): Updated character description (optional)
            image_file: File object for new character portrait (optional)
            remove_image (bool): Whether to remove the existing image (optional)

        Returns:
            Character: The updated character

        Raises:
            ValueError: If user is not the campaign owner
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if campaign.owner_id != user.id:
            raise ValueError('Only campaign owner can update characters')

        character = Character.query.filter_by(id=character_id, campaign_id=campaign_id).first_or_404()

        if name:
            character.name = name
        if race:
            character.race = race
        if character_class:
            character.character_class = character_class
        if description is not None:
            character.description = description

        if remove_image:
            CharactersService._delete_character_image(character.image_url)
            character.image_url = None
        elif image_file:
            CharactersService._delete_character_image(character.image_url)
            character.image_url = CharactersService._save_character_image(image_file, campaign_id)

        db.session.commit()

        return character

    @staticmethod
    def delete_character(campaign_id, character_id, user):
        """
        Delete a character.

        Only the campaign owner can delete characters.

        Args:
            campaign_id (int): The ID of the campaign
            character_id (int): The ID of the character
            user: The user requesting the deletion

        Raises:
            ValueError: If user is not the campaign owner
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if campaign.owner_id != user.id:
            raise ValueError('Only campaign owner can delete characters')

        character = Character.query.filter_by(id=character_id, campaign_id=campaign_id).first_or_404()

        if character.image_url:
            CharactersService._delete_character_image(character.image_url)

        db.session.delete(character)
        db.session.commit()

    @staticmethod
    def _save_character_image(image_file, campaign_id):
        """
        Save a character image file.

        Args:
            image_file: File object to save
            campaign_id (int): The ID of the campaign

        Returns:
            str: The URL path to the saved image
        """
        if not image_file or not image_file.filename or not CharactersService.allowed_file(image_file.filename):
            return None

        filename = secure_filename(image_file.filename)
        timestamp = str(int(os.path.getmtime(__file__) * 1000))
        unique_filename = f"character_{campaign_id}_{timestamp}_{filename}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        image_file.save(filepath)

        return f"/uploads/{unique_filename}"

    @staticmethod
    def _delete_character_image(image_url):
        """
        Delete a character image file.

        Args:
            image_url (str): The URL path to the image
        """
        if not image_url:
            return

        old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                     image_url.replace('/uploads/', ''))
        if os.path.exists(old_image_path):
            os.remove(old_image_path)
