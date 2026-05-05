"""Service for post viewed status operations."""

from app import db
from app.models import Post, Campaign, PostViewedStatus


class PostsViewedStatusService:
    """Service for handling post viewed status business logic."""

    @staticmethod
    def is_campaign_member(campaign, user):
        """
        Check if user is a campaign member (not owner).

        Args:
            campaign: The campaign object to check access for
            user: The user object to verify

        Returns:
            bool: True if user is a member (not owner), False otherwise
        """
        if campaign.owner_id == user.id:
            return False
        is_member = campaign.members.filter_by(id=user.id).first() is not None
        return is_member

    @staticmethod
    def get_campaign_viewed_status(campaign_id, user):
        """
        Get viewed status for all posts in a campaign for a user.

        Only campaign members (not owners) can access viewed status.
        Returns a list of post IDs that have been viewed by the current user.

        Args:
            campaign_id (int): The ID of the campaign
            user: The user requesting the information

        Returns:
            list: List of viewed post IDs

        Raises:
            ValueError: If user is not a campaign member or is the owner
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if not PostsViewedStatusService.is_campaign_member(campaign, user):
            raise ValueError('Unauthorized - viewed status only available to campaign members')

        viewed_posts = db.session.query(PostViewedStatus.c.post_id)\
            .filter(PostViewedStatus.c.user_id == user.id)\
            .join(Post, PostViewedStatus.c.post_id == Post.id)\
            .filter(Post.campaign_id == campaign_id)\
            .all()

        viewed_post_ids = [post_id for (post_id,) in viewed_posts]

        return viewed_post_ids

    @staticmethod
    def mark_post_viewed(post_id, user):
        """
        Mark a post as viewed for a user.

        Only campaign members (not owners) can mark posts as viewed.
        Creates or updates an entry in the PostViewedStatus table.

        Args:
            post_id (int): The ID of the post to mark as viewed
            user: The user marking the post as viewed

        Returns:
            bool: True if marked, False if already marked

        Raises:
            ValueError: If user is not a campaign member or is the owner
        """
        post = Post.query.get_or_404(post_id)
        campaign = Campaign.query.get(post.campaign_id)

        if not PostsViewedStatusService.is_campaign_member(campaign, user):
            raise ValueError('Unauthorized - only campaign members can mark posts as viewed')

        existing = db.session.query(PostViewedStatus)\
            .filter(PostViewedStatus.c.user_id == user.id)\
            .filter(PostViewedStatus.c.post_id == post_id)\
            .first()

        if existing:
            return False

        db.session.execute(
            PostViewedStatus.insert().values(
                user_id=user.id,
                post_id=post_id
            )
        )
        db.session.commit()

        return True
