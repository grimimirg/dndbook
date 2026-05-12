"""
Unit tests for PostsViewedStatusService using GIVEN-WHEN-THEN pattern.
"""
import pytest
from app import db
from app.services.posts_viewed_status_service import PostsViewedStatusService
from app.models import Campaign, User, Post, PostViewedStatus


def test_is_campaign_member_as_owner(app):
    """GIVEN a campaign owned by a user
    WHEN checking if the user is a member
    THEN the function should return False (owner is not a member)
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
        assert PostsViewedStatusService.is_campaign_member(campaign, user) == False


def test_is_campaign_member_as_member(app):
    """GIVEN a campaign where a user is a member
    WHEN checking if the user is a member
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
        assert PostsViewedStatusService.is_campaign_member(campaign, member) == True


def test_is_campaign_member_not_member(app):
    """GIVEN a campaign where a user is not a member
    WHEN checking if the user is a member
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
        assert PostsViewedStatusService.is_campaign_member(campaign, other) == False


def test_get_campaign_viewed_status_as_member(app):
    """GIVEN a campaign member with a viewed post
    WHEN retrieving viewed status for the campaign
    THEN the viewed post IDs should be returned
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
        
        post = Post(
            campaign_id=campaign.id,
            author_id=owner.id,
            title='Test Post',
            content='Test content'
        )
        db.session.add(post)
        db.session.commit()
        
        db.session.execute(
            PostViewedStatus.insert().values(
                user_id=member.id,
                post_id=post.id
            )
        )
        db.session.commit()
        
        # WHEN
        viewed_posts = PostsViewedStatusService.get_campaign_viewed_status(campaign.id, member)
        
        # THEN
        assert len(viewed_posts) == 1
        assert viewed_posts[0] == post.id


def test_get_campaign_viewed_status_as_owner(app):
    """GIVEN a campaign owned by a user
    WHEN the owner attempts to retrieve viewed status
    THEN access should be denied with 'Unauthorized - viewed status only available to campaign members' error
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
        with pytest.raises(ValueError, match='Unauthorized - viewed status only available to campaign members'):
            PostsViewedStatusService.get_campaign_viewed_status(campaign.id, owner)


def test_get_campaign_viewed_status_not_member(app):
    """GIVEN a campaign where a user is not a member
    WHEN the user attempts to retrieve viewed status
    THEN access should be denied with 'Unauthorized - viewed status only available to campaign members' error
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
        with pytest.raises(ValueError, match='Unauthorized - viewed status only available to campaign members'):
            PostsViewedStatusService.get_campaign_viewed_status(campaign.id, other)


def test_mark_post_viewed_success(app):
    """GIVEN a campaign member and a post
    WHEN marking the post as viewed
    THEN the post should be marked as viewed successfully
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
        
        post = Post(
            campaign_id=campaign.id,
            author_id=owner.id,
            title='Test Post',
            content='Test content'
        )
        db.session.add(post)
        db.session.commit()
        
        # WHEN
        result = PostsViewedStatusService.mark_post_viewed(post.id, member)
        
        # THEN
        assert result == True


def test_mark_post_viewed_already_viewed(app):
    """GIVEN a campaign member with an already viewed post
    WHEN attempting to mark the post as viewed again
    THEN the function should return False
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
        
        post = Post(
            campaign_id=campaign.id,
            author_id=owner.id,
            title='Test Post',
            content='Test content'
        )
        db.session.add(post)
        db.session.commit()
        
        PostsViewedStatusService.mark_post_viewed(post.id, member)
        
        # WHEN
        result = PostsViewedStatusService.mark_post_viewed(post.id, member)
        
        # THEN
        assert result == False


def test_mark_post_viewed_as_owner(app):
    """GIVEN a campaign owner and a post
    WHEN the owner attempts to mark the post as viewed
    THEN marking should be denied with 'Unauthorized - only campaign members can mark posts as viewed' error
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
        
        post = Post(
            campaign_id=campaign.id,
            author_id=owner.id,
            title='Test Post',
            content='Test content'
        )
        db.session.add(post)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Unauthorized - only campaign members can mark posts as viewed'):
            PostsViewedStatusService.mark_post_viewed(post.id, owner)


def test_mark_post_viewed_not_member(app):
    """GIVEN a campaign where a user is not a member and a post
    WHEN the user attempts to mark the post as viewed
    THEN marking should be denied with 'Unauthorized - only campaign members can mark posts as viewed' error
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
        
        post = Post(
            campaign_id=campaign.id,
            author_id=owner.id,
            title='Test Post',
            content='Test content'
        )
        db.session.add(post)
        db.session.commit()
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Unauthorized - only campaign members can mark posts as viewed'):
            PostsViewedStatusService.mark_post_viewed(post.id, other)
