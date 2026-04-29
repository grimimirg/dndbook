from datetime import datetime
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import and_, or_

from app import db
from app.jwt.jwt_utils import token_required
from app.models import CampaignInvite, Campaign, User, campaign_members, Notification
from app.events.socketio_events import send_invite_notification, send_player_joined_notification, send_notification

bp = Blueprint('invites', __name__, url_prefix='/api/invites')


@bp.route('', methods=['GET'])
@token_required
def get_invites(current_user):
    """
    Get all pending invites for the authenticated user.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        
    Returns:
        JSON response with:
        - 200: Array of pending invite objects
    """
    invites = CampaignInvite.query.filter_by(
        invitee_id=current_user.id,
        status='pending'
    ).all()

    return jsonify([invite.to_dict() for invite in invites]), 200


@bp.route('/<int:invite_id>/accept', methods=['POST'])
@token_required
def accept_invite(current_user, invite_id):
    """
    Accept a campaign invite.
    
    Adds the user to the campaign members and sends a Socket.IO notification
    to the campaign owner.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        invite_id (int): The ID of the invite to accept
        
    Returns:
        JSON response with:
        - 200: Success message and campaign data
        - 400: Invite already processed
        - 403: User is not the invitee
        - 404: Invite or campaign not found
    """
    invite = CampaignInvite.query.get_or_404(invite_id)

    if invite.invitee_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if invite.status != 'pending':
        return jsonify({'error': 'Invite already processed'}), 400

    campaign = Campaign.query.get(invite.campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404

    existing_member = db.session.execute(
        db.select(campaign_members).where(
            and_(
                campaign_members.c.user_id == current_user.id,
                campaign_members.c.campaign_id == campaign.id
            )
        )
    ).first()

    if not existing_member:
        stmt = campaign_members.insert().values(
            user_id=current_user.id,
            campaign_id=campaign.id
        )
        db.session.execute(stmt)

    db.session.delete(invite)
    db.session.commit()

    send_player_joined_notification(campaign.owner_id, {
        'campaign_id': campaign.id,
        'campaign_name': campaign.name,
        'player_id': current_user.id,
        'player_username': current_user.username
    })

    return jsonify({
        'message': 'Invite accepted',
        'campaign': campaign.to_dict()
    }), 200


@bp.route('/<int:invite_id>/reject', methods=['POST'])
@token_required
def reject_invite(current_user, invite_id):
    """
    Reject a campaign invite.
    
    Deletes the invite from the database.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        invite_id (int): The ID of the invite to reject
        
    Returns:
        JSON response with:
        - 200: Success message
        - 400: Invite already processed
        - 403: User is not the invitee
        - 404: Invite not found
    """
    invite = CampaignInvite.query.get_or_404(invite_id)

    if invite.invitee_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    if invite.status != 'pending':
        return jsonify({'error': 'Invite already processed'}), 400

    db.session.delete(invite)
    db.session.commit()

    return jsonify({'message': 'Invite rejected'}), 200


@bp.route('/campaign/<int:campaign_id>', methods=['POST'])
@token_required
def invite_users(current_user, campaign_id):
    """
    Invite multiple users to a campaign.
    
    Only the campaign owner can send invites.
    Sends Socket.IO notifications to invited users.
    
    Expected JSON payload:
        - user_ids (list): Array of user IDs to invite
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        
    Returns:
        JSON response with:
        - 200: Success with invited count and any errors
        - 400: No users specified
        - 403: User is not the campaign owner
        - 404: Campaign not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Only campaign owner can invite users'}), 403

    data = request.get_json()
    user_ids = data.get('user_ids', [])

    if not user_ids:
        return jsonify({'error': 'No users specified'}), 400

    invited_count = 0
    errors = []

    for user_id in user_ids:
        user = User.query.get(user_id)
        if not user:
            errors.append(f'User {user_id} not found')
            continue

        existing_member = db.session.execute(
            db.select(campaign_members).where(
                and_(
                    campaign_members.c.user_id == user_id,
                    campaign_members.c.campaign_id == campaign_id
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
            inviter_id=current_user.id,
            invitee_id=user_id,
            status='pending'
        )
        db.session.add(invite)
        db.session.flush()

        # Create notification entry in unified notification system
        notification = Notification(
            user_id=user_id,
            campaign_id=campaign_id,
            notification_type='invite',
            title=f'Campaign invite: {campaign.name}',
            message=f'{current_user.username} invited you to join the campaign "{campaign.name}".',
            related_post_id=None
        )
        db.session.add(notification)

        # Send WebSocket notification to the invited user
        send_notification(user_id)

        send_invite_notification(user_id, {
            'id': invite.id,
            'campaign_id': campaign_id,
            'campaign_name': campaign.name,
            'inviter_id': current_user.id,
            'inviter_username': current_user.username
        })

        invited_count += 1

    db.session.commit()

    return jsonify({
        'message': f'{invited_count} invite(s) sent',
        'invited_count': invited_count,
        'errors': errors
    }), 200


@bp.route('/available-users/<int:campaign_id>', methods=['GET'])
@token_required
def get_available_users(current_user, campaign_id):
    """
    Get all users available to invite to a campaign.
    
    Returns users who are not the owner, not current members,
    and do not have pending invites.
    Only the campaign owner can access this endpoint.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        
    Returns:
        JSON response with:
        - 200: Array of available user objects (id, username, email)
        - 403: User is not the campaign owner
        - 404: Campaign not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

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

    return jsonify([
        {'id': u.id, 'username': u.username, 'email': u.email}
        for u in available_users
    ]), 200
