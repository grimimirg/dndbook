"""
Unit tests for InvitesService using GIVEN-WHEN-THEN pattern.
"""
import pytest
from app import db
from app.services.invites_service import InvitesService
from app.models import Campaign, User, CampaignInvite, CampaignMembers


def test_get_pending_invites_empty(app):
    """GIVEN a user with no pending invites
    WHEN retrieving pending invites
    THEN an empty list should be returned
    """
    with app.app_context():
        # GIVEN
        user = User(username='testuser', email='test@example.com')
        user.set_password('password123')
        db.session.add(user)
        db.session.commit()
        
        # WHEN
        invites = InvitesService.get_pending_invites(user)
        
        # THEN
        assert invites == []


def test_get_pending_invites_with_invites(app):
    """GIVEN a user with pending invites
    WHEN retrieving pending invites
    THEN the invites should be returned
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        invitee = User(username='invitee', email='invitee@example.com')
        invitee.set_password('password123')
        db.session.add(invitee)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        invite = CampaignInvite(
            campaign_id=campaign.id,
            inviter_id=owner.id,
            invitee_id=invitee.id,
            status='pending'
        )
        db.session.add(invite)
        db.session.commit()
        
        # WHEN
        invites = InvitesService.get_pending_invites(invitee)
        
        # THEN
        assert len(invites) == 1
        assert invites[0]['campaign_id'] == campaign.id


def test_accept_invite_success(app):
    """GIVEN a user with a pending invite
    WHEN accepting the invite
    THEN the user should join the campaign and invite should be deleted
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        invitee = User(username='invitee', email='invitee@example.com')
        invitee.set_password('password123')
        db.session.add(invitee)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        invite = CampaignInvite(
            campaign_id=campaign.id,
            inviter_id=owner.id,
            invitee_id=invitee.id,
            status='pending'
        )
        db.session.add(invite)
        db.session.commit()
        
        # WHEN
        result = InvitesService.accept_invite(invite.id, invitee)
        
        # THEN
        assert result['id'] == campaign.id
        assert result['name'] == 'Test Campaign'
        
        deleted_invite = CampaignInvite.query.get(invite.id)
        assert deleted_invite is None


def test_accept_invite_unauthorized(app):
    """GIVEN an invite for one user
    WHEN another user attempts to accept it
    THEN acceptance should be denied with 'Unauthorized' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        invitee = User(username='invitee', email='invitee@example.com')
        invitee.set_password('password123')
        db.session.add(invitee)
        
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
        
        invite = CampaignInvite(
            campaign_id=campaign.id,
            inviter_id=owner.id,
            invitee_id=invitee.id,
            status='pending'
        )
        db.session.add(invite)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Unauthorized'):
            InvitesService.accept_invite(invite.id, other)


def test_accept_invite_already_processed(app):
    """GIVEN an already processed invite
    WHEN attempting to accept it
    THEN acceptance should fail with 'Invite already processed' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        invitee = User(username='invitee', email='invitee@example.com')
        invitee.set_password('password123')
        db.session.add(invitee)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        invite = CampaignInvite(
            campaign_id=campaign.id,
            inviter_id=owner.id,
            invitee_id=invitee.id,
            status='accepted'
        )
        db.session.add(invite)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Invite already processed'):
            InvitesService.accept_invite(invite.id, invitee)


def test_reject_invite_success(app):
    """GIVEN a user with a pending invite
    WHEN rejecting the invite
    THEN the invite should be deleted
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        invitee = User(username='invitee', email='invitee@example.com')
        invitee.set_password('password123')
        db.session.add(invitee)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        invite = CampaignInvite(
            campaign_id=campaign.id,
            inviter_id=owner.id,
            invitee_id=invitee.id,
            status='pending'
        )
        db.session.add(invite)
        db.session.commit()
        
        # WHEN
        InvitesService.reject_invite(invite.id, invitee)
        
        # THEN
        deleted_invite = CampaignInvite.query.get(invite.id)
        assert deleted_invite is None


def test_invite_users_success(app):
    """GIVEN a campaign owner and users to invite
    WHEN inviting users to the campaign
    THEN invites should be created successfully
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        user1 = User(username='user1', email='user1@example.com')
        user1.set_password('password123')
        db.session.add(user1)
        
        user2 = User(username='user2', email='user2@example.com')
        user2.set_password('password123')
        db.session.add(user2)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN
        result = InvitesService.invite_users(campaign.id, [user1.id, user2.id], owner)
        
        # THEN
        assert result['invited_count'] == 2
        assert len(result['errors']) == 0


def test_invite_users_unauthorized(app):
    """GIVEN a campaign owned by one user
    WHEN another user attempts to invite users
    THEN invitation should be denied with 'Only campaign owner can invite users' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        other = User(username='other', email='other@example.com')
        other.set_password('password123')
        db.session.add(other)
        
        user1 = User(username='user1', email='user1@example.com')
        user1.set_password('password123')
        db.session.add(user1)
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
        with pytest.raises(ValueError, match='Only campaign owner can invite users'):
            InvitesService.invite_users(campaign.id, [user1.id], other)


def test_invite_users_no_users(app):
    """GIVEN a campaign owner with no user IDs
    WHEN attempting to invite users
    THEN invitation should fail with 'No users specified' error
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
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
        with pytest.raises(ValueError, match='No users specified'):
            InvitesService.invite_users(campaign.id, [], owner)


def test_get_available_users_as_owner(app):
    """GIVEN a campaign owned by a user with available users
    WHEN retrieving available users
    THEN the available users should be returned
    """
    with app.app_context():
        # GIVEN
        owner = User(username='owner', email='owner@example.com')
        owner.set_password('password123')
        db.session.add(owner)
        
        available = User(username='available', email='available@example.com')
        available.set_password('password123')
        db.session.add(available)
        db.session.commit()
        
        campaign = Campaign(
            name='Test Campaign',
            description='Test description',
            owner_id=owner.id,
            character_creation_mode='optional'
        )
        db.session.add(campaign)
        db.session.commit()
        
        # WHEN
        users = InvitesService.get_available_users(campaign.id, owner)
        
        # THEN
        assert len(users) == 1
        assert users[0]['username'] == 'available'


def test_get_available_users_unauthorized(app):
    """GIVEN a campaign owned by one user
    WHEN another user attempts to retrieve available users
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
            InvitesService.get_available_users(campaign.id, other)
