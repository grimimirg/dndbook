"""
Unit tests for CampaignsService using GIVEN-WHEN-THEN pattern.
"""
import pytest
from app import db
from app.services.campaigns_service import CampaignsService
from app.models import Campaign, User


def test_get_user_campaigns_empty(app):
    """GIVEN a user with no campaigns
    WHEN retrieving the user's campaigns
    THEN both owned and shared campaign lists should be empty
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # WHEN
        result = CampaignsService.get_user_campaigns(user)
        
        # THEN
        assert result['owned'] == []
        assert result['shared'] == []


def test_get_user_campaigns_with_owned(app):
    """GIVEN a user with an owned campaign
    WHEN retrieving the user's campaigns
    THEN the owned campaigns list should contain the campaign
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
        result = CampaignsService.get_user_campaigns(user)
        
        # THEN
        assert len(result['owned']) == 1
        assert result['owned'][0]['name'] == 'Test Campaign'
        assert result['shared'] == []


def test_create_campaign_success(app):
    """GIVEN a user and campaign details
    WHEN creating a new campaign
    THEN the campaign should be created with the specified details
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        campaign_name = 'Test Campaign'
        description = 'Test description'
        character_creation_mode = 'optional'
        
        # WHEN
        campaign = CampaignsService.create_campaign(
            user=user,
            name=campaign_name,
            description=description,
            character_creation_mode=character_creation_mode
        )
        
        # THEN
        assert campaign is not None
        assert campaign.name == campaign_name
        assert campaign.description == description
        assert campaign.owner_id == user.id
        assert campaign.character_creation_mode == character_creation_mode


def test_create_campaign_invalid_mode(app):
    """GIVEN a user and invalid character creation mode
    WHEN attempting to create a campaign
    THEN campaign creation should fail with 'Invalid character_creation_mode' error
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Invalid character_creation_mode'):
            CampaignsService.create_campaign(
                user=user,
                name='Test Campaign',
                character_creation_mode='invalid_mode'
            )


def test_get_campaign_as_owner(app):
    """GIVEN a campaign owned by a user
    WHEN the owner retrieves the campaign
    THEN the campaign should be returned successfully
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
        retrieved = CampaignsService.get_campaign(campaign.id, user)
        
        # THEN
        assert retrieved.id == campaign.id
        assert retrieved.name == 'Test Campaign'


def test_get_campaign_unauthorized(app):
    """GIVEN a campaign owned by one user
    WHEN another user attempts to retrieve it
    THEN access should be denied with 'Unauthorized' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        other_user = User(username='other', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
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
            CampaignsService.get_campaign(campaign.id, other_user)


def test_update_campaign_as_owner(app):
    """GIVEN a campaign owned by a user
    WHEN the owner updates the campaign details
    THEN the campaign should be updated successfully
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
        updated = CampaignsService.update_campaign(
            campaign_id=campaign.id,
            user=user,
            name='Updated Campaign',
            description='Updated description'
        )
        
        # THEN
        assert updated.name == 'Updated Campaign'
        assert updated.description == 'Updated description'


def test_update_campaign_unauthorized(app):
    """GIVEN a campaign owned by one user
    WHEN another user attempts to update it
    THEN update should be denied with 'Unauthorized' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        other_user = User(username='other', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
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
            CampaignsService.update_campaign(
                campaign_id=campaign.id,
                user=other_user,
                name='Updated Campaign'
            )


def test_delete_campaign_as_owner(app):
    """GIVEN a campaign owned by a user
    WHEN the owner deletes the campaign
    THEN the campaign should be removed from the database
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
        
        campaign_id = campaign.id
        
        # WHEN
        CampaignsService.delete_campaign(campaign_id, user)
        
        # THEN
        deleted = Campaign.query.get(campaign_id)
        assert deleted is None


def test_delete_campaign_unauthorized(app):
    """GIVEN a campaign owned by one user
    WHEN another user attempts to delete it
    THEN deletion should be denied with 'Unauthorized' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        other_user = User(username='other', email='other@example.com')
        other_user.set_password('password123')
        db.session.add(other_user)
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
            CampaignsService.delete_campaign(campaign.id, other_user)
