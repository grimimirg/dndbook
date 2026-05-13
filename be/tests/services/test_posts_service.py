"""
Unit tests for PostsService using GIVEN-WHEN-THEN pattern.
"""
import pytest
from app import db
from app.services.posts_service import PostsService
from app.models import Campaign, User, Post


def test_allowed_file_valid_extensions(app):
    """GIVEN valid image file extensions
    WHEN checking if file is allowed
    THEN the function should return True
    """
    # GIVEN & WHEN & THEN
    assert PostsService.allowed_file('test.png') == True
    assert PostsService.allowed_file('test.jpg') == True
    assert PostsService.allowed_file('test.jpeg') == True
    assert PostsService.allowed_file('test.gif') == True
    assert PostsService.allowed_file('test.webp') == True


def test_allowed_file_invalid_extensions(app):
    """GIVEN invalid image file extensions
    WHEN checking if file is allowed
    THEN the function should return False
    """
    # GIVEN & WHEN & THEN
    assert PostsService.allowed_file('test.pdf') == False
    assert PostsService.allowed_file('test.txt') == False
    assert PostsService.allowed_file('test.doc') == False
    assert PostsService.allowed_file('test') == False


def test_allowed_file_case_insensitive(app):
    """GIVEN file extensions in different cases
    WHEN checking if file is allowed
    THEN the function should be case insensitive
    """
    # GIVEN & WHEN & THEN
    assert PostsService.allowed_file('test.PNG') == True
    assert PostsService.allowed_file('test.JPG') == True
    assert PostsService.allowed_file('test.WebP') == True


def test_can_access_campaign_as_owner(app):
    """GIVEN a campaign owned by a user
    WHEN checking if the user can access the campaign
    THEN the function should return True
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
        assert PostsService.can_access_campaign(campaign, user) == True


def test_can_access_campaign_as_member(app):
    """GIVEN a campaign where a user is a member
    WHEN checking if the user can access the campaign
    THEN the function should return True
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        member = User(username='member', email='member@example.com')
        member.set_password('password123')
        db.session.add(member)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        campaign.members.append(member)
        db.session.commit()
        
        # WHEN & THEN
        assert PostsService.can_access_campaign(campaign, member) == True


def test_can_access_campaign_unauthorized(app):
    """GIVEN a campaign where a user is not a member
    WHEN checking if the user can access the campaign
    THEN the function should return False
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
        assert PostsService.can_access_campaign(campaign, other) == False
