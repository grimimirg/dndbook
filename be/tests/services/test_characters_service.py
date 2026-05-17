"""
Unit tests for CharactersService using GIVEN-WHEN-THEN pattern.
"""
import pytest
from app import db
from app.services.characters_service import CharactersService
from app.models import Campaign, User, Character


def test_allowed_file_valid_extensions(app):
    """GIVEN valid image file extensions
    WHEN checking if file is allowed
    THEN the function should return True
    """
    # GIVEN & WHEN & THEN
    assert CharactersService.allowed_file('test.png') == True
    assert CharactersService.allowed_file('test.jpg') == True
    assert CharactersService.allowed_file('test.jpeg') == True
    assert CharactersService.allowed_file('test.gif') == True
    assert CharactersService.allowed_file('test.webp') == True


def test_allowed_file_invalid_extensions(app):
    """GIVEN invalid image file extensions
    WHEN checking if file is allowed
    THEN the function should return False
    """
    # GIVEN & WHEN & THEN
    assert CharactersService.allowed_file('test.pdf') == False
    assert CharactersService.allowed_file('test.txt') == False
    assert CharactersService.allowed_file('test.doc') == False


def test_get_characters_empty(app):
    """GIVEN a campaign with no characters
    WHEN retrieving characters for the campaign
    THEN an empty list should be returned
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN
        characters = CharactersService.get_characters(campaign.id, user)
        
        # THEN
        assert characters == []


def test_get_characters_as_owner(app):
    """GIVEN a campaign owned by a user with a character
    WHEN the owner retrieves characters
    THEN the character list should contain the character
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        character = Character(
            campaign_id=campaign.id,
            name='Test Character',
            race='Human',
            character_class='Fighter'
        )
        db.session.add(character)
        db.session.commit()
        
        # WHEN
        characters = CharactersService.get_characters(campaign.id, user)
        
        # THEN
        assert len(characters) == 1
        assert characters[0]['name'] == 'Test Character'


def test_get_characters_unauthorized(app):
    """GIVEN a campaign owned by one user
    WHEN another user attempts to retrieve characters
    THEN access should be denied with 'Unauthorized' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        other = User(username='other', email='other@example.com')
        other.set_password('password123')
        db.session.add(other)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Unauthorized'):
            CharactersService.get_characters(campaign.id, other)


def test_create_character_success(app):
    """GIVEN a campaign owner and character details
    WHEN creating a new character
    THEN the character should be created with the specified details
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN
        character = CharactersService.create_character(
            campaign_id=campaign.id,
            user=user,
            name='Test Character',
            race='Human',
            character_class='Fighter',
            description='A brave fighter'
        )
        
        # THEN
        assert character is not None
        assert character.name == 'Test Character'
        assert character.race == 'Human'
        assert character.character_class == 'Fighter'
        assert character.description == 'A brave fighter'


def test_create_character_unauthorized(app):
    """GIVEN a campaign owned by one user
    WHEN a non-member user attempts to create a character
    THEN creation should be denied with 'Unauthorized' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        other = User(username='other', email='other@example.com')
        other.set_password('password123')
        db.session.add(other)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Unauthorized'):
            CharactersService.create_character(
                campaign_id=campaign.id,
                user=other,
                name='Test Character',
                race='Human',
                character_class='Fighter'
            )


def test_create_character_missing_required_fields(app):
    """GIVEN a campaign owner and missing required character fields
    WHEN attempting to create a character
    THEN creation should fail with 'Name, race, and class are required' error
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Name, race, and class are required'):
            CharactersService.create_character(
                campaign_id=campaign.id,
                user=user,
                name='',
                race='Human',
                character_class='Fighter'
            )


def test_create_predefined_character_as_owner(app):
    """GIVEN a campaign owner in predefined mode
    WHEN creating a predefined character
    THEN the character should be created with is_predefined set to True
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='predefined'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN
        character = CharactersService.create_character(
            campaign_id=campaign.id,
            user=user,
            name='Test Character',
            race='Human',
            character_class='Fighter',
            is_predefined=True
        )
        
        # THEN
        assert character.is_predefined == True


def test_get_character_as_owner(app):
    """GIVEN a campaign owned by a user with a character
    WHEN the owner retrieves the character
    THEN the character should be returned successfully
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        character = Character(
            campaign_id=campaign.id,
            name='Test Character',
            race='Human',
            character_class='Fighter'
        )
        db.session.add(character)
        db.session.commit()
        
        # WHEN
        retrieved = CharactersService.get_character(campaign.id, character.id, user)
        
        # THEN
        assert retrieved.id == character.id
        assert retrieved.name == 'Test Character'


def test_delete_character_as_owner(app):
    """GIVEN a campaign owned by a user with a character
    WHEN the owner deletes the character
    THEN the character should be removed from the database
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        character = Character(
            campaign_id=campaign.id,
            name='Test Character',
            race='Human',
            character_class='Fighter'
        )
        db.session.add(character)
        db.session.commit()
        
        character_id = character.id
        
        # WHEN
        CharactersService.delete_character(campaign.id, character_id, user)
        
        # THEN
        deleted = Character.query.get(character_id)
        assert deleted is None


def test_delete_character_unauthorized(app):
    """GIVEN a campaign owned by one user with a character
    WHEN another user attempts to delete the character
    THEN deletion should be denied with 'Only campaign owner can delete characters' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        other = User(username='other', email='other@example.com')
        other.set_password('password123')
        db.session.add(other)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        character = Character(
            campaign_id=campaign.id,
            name='Test Character',
            race='Human',
            character_class='Fighter'
        )
        db.session.add(character)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Only campaign owner can delete characters'):
            CharactersService.delete_character(campaign.id, character.id, other)
