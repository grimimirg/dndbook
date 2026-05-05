"""Service for campaign operations."""

from sqlalchemy import and_

from app import db
from app.models import Campaign, CampaignInvite, CampaignMembers


class CampaignsService:
    """Service for handling campaign business logic."""

    @staticmethod
    def get_user_campaigns(user):
        """
        Get all campaigns for a user.

        Returns campaigns owned by the user and campaigns where the user is a member.

        Args:
            user: The user object

        Returns:
            dict: Object containing 'owned' and 'shared' campaign arrays
        """
        owned_campaigns = Campaign.query.filter_by(owner_id=user.id).all()
        member_campaigns = [c for c in user.member_campaigns if c.owner_id != user.id]

        return {
            'owned': [campaign.to_dict() for campaign in owned_campaigns],
            'shared': [campaign.to_dict() for campaign in member_campaigns]
        }

    @staticmethod
    def create_campaign(user, name, description=''):
        """
        Create a new campaign.

        Args:
            user: The user who will own the campaign
            name (str): Campaign name
            description (str): Campaign description

        Returns:
            Campaign: The created campaign
        """
        campaign = Campaign(
            name=name,
            description=description,
            owner_id=user.id
        )

        db.session.add(campaign)
        db.session.commit()

        return campaign

    @staticmethod
    def get_campaign(campaign_id, user):
        """
        Get a specific campaign by ID.

        User must be either the campaign owner or a member to access.

        Args:
            campaign_id (int): The ID of the campaign
            user: The user requesting access

        Returns:
            Campaign: The campaign object

        Raises:
            ValueError: If user is not authorized
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        is_member = campaign.members.filter_by(id=user.id).first() is not None
        if campaign.owner_id != user.id and not is_member:
            raise ValueError('Unauthorized')

        return campaign

    @staticmethod
    def update_campaign(campaign_id, user, name=None, description=None):
        """
        Update a campaign.

        Only the campaign owner can update the campaign.

        Args:
            campaign_id (int): The ID of the campaign
            user: The user requesting the update
            name (str): Updated campaign name (optional)
            description (str): Updated campaign description (optional)

        Returns:
            Campaign: The updated campaign

        Raises:
            ValueError: If user is not the campaign owner
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if campaign.owner_id != user.id:
            raise ValueError('Unauthorized')

        if name:
            campaign.name = name
        if description is not None:
            campaign.description = description

        db.session.commit()

        return campaign

    @staticmethod
    def delete_campaign(campaign_id, user):
        """
        Delete a campaign.

        Only the campaign owner can delete the campaign.

        Args:
            campaign_id (int): The ID of the campaign
            user: The user requesting the deletion

        Raises:
            ValueError: If user is not the campaign owner
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if campaign.owner_id != user.id:
            raise ValueError('Unauthorized')

        db.session.delete(campaign)
        db.session.commit()

    @staticmethod
    def get_campaign_members(campaign_id, user):
        """
        Get all members of a campaign and pending invites.

        User must be either the campaign owner or a member to access.
        Pending invites are only returned if the user is the campaign owner.

        Args:
            campaign_id (int): The ID of the campaign
            user: The user requesting the information

        Returns:
            dict: Object containing 'members' array and 'pending_invites' array

        Raises:
            ValueError: If user is not authorized
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        is_member = campaign.members.filter_by(id=user.id).first() is not None
        if campaign.owner_id != user.id and not is_member:
            raise ValueError('Unauthorized')

        members = [{'id': m.id, 'username': m.username, 'email': m.email} for m in campaign.members.all()]

        pending_invites = []
        if campaign.owner_id == user.id:
            invites = CampaignInvite.query.filter_by(
                campaign_id=campaign_id,
                status='pending'
            ).all()
            pending_invites = [invite.to_dict() for invite in invites]

        return {
            'members': members,
            'pending_invites': pending_invites
        }

    @staticmethod
    def remove_campaign_member(campaign_id, user_id, requesting_user):
        """
        Remove a member from a campaign.

        Only the campaign owner can remove members.
        The campaign owner cannot be removed.

        Args:
            campaign_id (int): The ID of the campaign
            user_id (int): The ID of the user to remove
            requesting_user: The user requesting the removal

        Raises:
            ValueError: If user is not the campaign owner, trying to remove owner, or member not found
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if campaign.owner_id != requesting_user.id:
            raise ValueError('Only campaign owner can remove members')

        if user_id == campaign.owner_id:
            raise ValueError('Cannot remove campaign owner')

        stmt = db.select(CampaignMembers).where(
            and_(
                CampaignMembers.c.user_id == user_id,
                CampaignMembers.c.campaign_id == campaign_id
            )
        )
        existing_member = db.session.execute(stmt).first()

        if not existing_member:
            raise ValueError('User is not a member of this campaign')

        delete_stmt = CampaignMembers.delete().where(
            and_(
                CampaignMembers.c.user_id == user_id,
                CampaignMembers.c.campaign_id == campaign_id
            )
        )
        db.session.execute(delete_stmt)
        db.session.commit()

    @staticmethod
    def cancel_invite(campaign_id, invite_id, requesting_user):
        """
        Cancel a pending campaign invite.

        Only the campaign owner can cancel invites.
        Only pending invites can be cancelled.

        Args:
            campaign_id (int): The ID of the campaign
            invite_id (int): The ID of the invite to cancel
            requesting_user: The user requesting the cancellation

        Raises:
            ValueError: If user is not the campaign owner, invite doesn't belong to campaign, or invite is not pending
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if campaign.owner_id != requesting_user.id:
            raise ValueError('Only campaign owner can cancel invites')

        invite = CampaignInvite.query.get_or_404(invite_id)

        if invite.campaign_id != campaign_id:
            raise ValueError('Invite does not belong to this campaign')

        if invite.status != 'pending':
            raise ValueError('Invite is not pending')

        db.session.delete(invite)
        db.session.commit()
