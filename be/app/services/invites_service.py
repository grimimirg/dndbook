"""Service for invite operations."""

from sqlalchemy import and_

from app import db
from app.models import CampaignInvite, Campaign, User, CampaignMembers, Notification
from app.events.socketio_events import send_invite_notification, send_player_joined_notification, send_notification


class InvitesService:
    """Service for handling invite business logic."""

    @staticmethod
    def get_pending_invites(user):
        """
        Get all pending invites for a user.

        Args:
            user: The user to get invites for

        Returns:
            list: Array of pending invite objects
        """
        invites = CampaignInvite.query.filter_by(
            invitee_id=user.id,
            status='pending'
        ).all()

        return [invite.to_dict() for invite in invites]

    @staticmethod
    def accept_invite(invite_id, user):
        """
        Accept a campaign invite.

        Adds the user to the campaign members and sends a Socket.IO notification
        to the campaign owner.

        Args:
            invite_id (int): The ID of the invite
            user: The user accepting the invite

        Returns:
            Campaign: The campaign the user joined

        Raises:
            ValueError: If user is not the invitee, invite already processed, or campaign not found
        """
        invite = CampaignInvite.query.get_or_404(invite_id)

        if invite.invitee_id != user.id:
            raise ValueError('Unauthorized')

        if invite.status != 'pending':
            raise ValueError('Invite already processed')

        campaign = Campaign.query.get(invite.campaign_id)
        if not campaign:
            raise ValueError('Campaign not found')

        existing_member = db.session.execute(
            db.select(CampaignMembers).where(
                and_(
                    CampaignMembers.c.user_id == user.id,
                    CampaignMembers.c.campaign_id == campaign.id
                )
            )
        ).first()

        if not existing_member:
            stmt = CampaignMembers.insert().values(
                user_id=user.id,
                campaign_id=campaign.id
            )
            db.session.execute(stmt)

        db.session.delete(invite)
        db.session.commit()

        send_player_joined_notification(campaign.owner_id, {
            'campaign_id': campaign.id,
            'campaign_name': campaign.name,
            'player_id': user.id,
            'player_username': user.username
        })

        return campaign

    @staticmethod
    def reject_invite(invite_id, user):
        """
        Reject a campaign invite.

        Deletes the invite from the database.

        Args:
            invite_id (int): The ID of the invite
            user: The user rejecting the invite

        Raises:
            ValueError: If user is not the invitee or invite already processed
        """
        invite = CampaignInvite.query.get_or_404(invite_id)

        if invite.invitee_id != user.id:
            raise ValueError('Unauthorized')

        if invite.status != 'pending':
            raise ValueError('Invite already processed')

        db.session.delete(invite)
        db.session.commit()

    @staticmethod
    def invite_users(campaign_id, user_ids, inviter):
        """
        Invite multiple users to a campaign.

        Only the campaign owner can send invites.
        Sends Socket.IO notifications to invited users.

        Args:
            campaign_id (int): The ID of the campaign
            user_ids (list): Array of user IDs to invite
            inviter: The user sending the invites

        Returns:
            dict: Object with invited_count and errors array

        Raises:
            ValueError: If user is not the campaign owner or no users specified
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if campaign.owner_id != inviter.id:
            raise ValueError('Only campaign owner can invite users')

        if not user_ids:
            raise ValueError('No users specified')

        invited_count = 0
        errors = []

        for user_id in user_ids:
            user = User.query.get(user_id)
            if not user:
                errors.append(f'User {user_id} not found')
                continue

            existing_member = db.session.execute(
                db.select(CampaignMembers).where(
                    and_(
                        CampaignMembers.c.user_id == user_id,
                        CampaignMembers.c.campaign_id == campaign_id
                    )
                )
            ).first()

            if existing_member:
                errors.append(f'User {user.username} is already a member')
                continue

            existing_invite = CampaignInvite.query.filter_by(
                campaign_id=campaign_id,
                invitee_id=user_id,
                status='pending'
            ).first()

            if existing_invite:
                errors.append(f'User {user.username} already has a pending invite')
                continue

            invite = CampaignInvite(
                campaign_id=campaign_id,
                inviter_id=inviter.id,
                invitee_id=user_id,
                status='pending'
            )
            db.session.add(invite)
            db.session.flush()

            notification = Notification(
                user_id=user_id,
                campaign_id=campaign_id,
                notification_type='invite',
                title=f'Campaign invite: {campaign.name}',
                message=f'{inviter.username} invited you to join the campaign "{campaign.name}".',
                related_post_id=None
            )
            db.session.add(notification)

            send_notification(user_id)

            send_invite_notification(user_id, {
                'id': invite.id,
                'campaign_id': campaign_id,
                'campaign_name': campaign.name,
                'inviter_id': inviter.id,
                'inviter_username': inviter.username
            })

            invited_count += 1

        db.session.commit()

        return {
            'invited_count': invited_count,
            'errors': errors
        }

    @staticmethod
    def get_available_users(campaign_id, requesting_user):
        """
        Get all users available to invite to a campaign.

        Returns users who are not the owner, not current members,
        and do not have pending invites.
        Only the campaign owner can access this endpoint.

        Args:
            campaign_id (int): The ID of the campaign
            requesting_user: The user requesting the information

        Returns:
            list: Array of available user objects (id, username, email)

        Raises:
            ValueError: If user is not the campaign owner
        """
        campaign = Campaign.query.get_or_404(campaign_id)

        if campaign.owner_id != requesting_user.id:
            raise ValueError('Unauthorized')

        member_ids = [m.id for m in campaign.members.all()]
        member_ids.append(campaign.owner_id)

        pending_invites = CampaignInvite.query.filter_by(
            campaign_id=campaign_id,
            status='pending'
        ).all()
        pending_user_ids = [inv.invitee_id for inv in pending_invites]

        exclude_ids = list(set(member_ids + pending_user_ids))

        available_users = User.query.filter(
            ~User.id.in_(exclude_ids)
        ).all()

        return [
            {'id': u.id, 'username': u.username, 'email': u.email}
            for u in available_users
        ]
