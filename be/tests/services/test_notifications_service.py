"""
Unit tests for NotificationsService using GIVEN-WHEN-THEN pattern.
"""
import pytest
from app import db
from app.services.notifications_service import NotificationsService
from app.models import User, Notification, Campaign


def test_get_notifications_empty(app):
    """GIVEN a user with no notifications
    WHEN retrieving notifications
    THEN an empty list should be returned
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # WHEN
        result = NotificationsService.get_notifications(user)
        
        # THEN
        assert result['notifications'] == []
        assert result['total'] == 0


def test_get_notifications_with_notifications(app):
    """GIVEN a user with notifications
    WHEN retrieving notifications
    THEN the notifications should be returned
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        notification = Notification(
            user_id=user.id,
            campaign_id=campaign.id,
            notification_type='invite',
            title='Test Notification',
            message='Test message'
        )
        db.session.add(notification)
        db.session.commit()
        
        # WHEN
        result = NotificationsService.get_notifications(user)
        
        # THEN
        assert len(result['notifications']) == 1
        assert result['notifications'][0]['title'] == 'Test Notification'
        assert result['total'] == 1


def test_get_unread_count(app):
    """GIVEN a user with notifications
    WHEN getting the unread notification count
    THEN the count should match the number of notifications
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        notification = Notification(
            user_id=user.id,
            campaign_id=campaign.id,
            notification_type='invite',
            title='Test Notification',
            message='Test message'
        )
        db.session.add(notification)
        db.session.commit()
        
        # WHEN
        count = NotificationsService.get_unread_count(user)
        
        # THEN
        assert count == 1


def test_get_unread_count_empty(app):
    """GIVEN a user with no notifications
    WHEN getting the unread notification count
    THEN the count should be 0
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # WHEN
        count = NotificationsService.get_unread_count(user)
        
        # THEN
        assert count == 0


def test_delete_notifications(app):
    """GIVEN a user with notifications
    WHEN deleting all notifications
    THEN all notifications should be removed
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=user.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        notification = Notification(
            user_id=user.id,
            campaign_id=campaign.id,
            notification_type='invite',
            title='Test Notification',
            message='Test message'
        )
        db.session.add(notification)
        db.session.commit()
        
        # WHEN
        deleted_count = NotificationsService.delete_notifications(user)
        
        # THEN
        assert deleted_count == 1
        
        count = NotificationsService.get_unread_count(user)
        assert count == 0


def test_delete_notifications_empty(app):
    """GIVEN a user with no notifications
    WHEN attempting to delete notifications
    THEN the deleted count should be 0
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # WHEN
        deleted_count = NotificationsService.delete_notifications(user)
        
        # THEN
        assert deleted_count == 0
