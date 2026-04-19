from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from app import db
from app.models import CampaignInvite, Campaign, User, campaign_members
from app.auth import token_required
from app.socketio_events import send_invite_notification, send_player_joined_notification
from sqlalchemy import and_, or_

bp = Blueprint('invites', __name__, url_prefix='/api/invites')

@bp.route('', methods=['GET'])
@token_required
def get_invites(current_user):
    invites = CampaignInvite.query.filter_by(
        invitee_id=current_user.id,
        status='pending'
    ).all()
    
    return jsonify([invite.to_dict() for invite in invites]), 200

@bp.route('/<int:invite_id>/accept', methods=['POST'])
@token_required
def accept_invite(current_user, invite_id):
    invite = CampaignInvite.query.get_or_404(invite_id)
    
    if invite.invitee_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if invite.status != 'pending':
        return jsonify({'error': 'Invite already processed'}), 400
    
    campaign = Campaign.query.get(invite.campaign_id)
    if not campaign:
        return jsonify({'error': 'Campaign not found'}), 404
    
    # Check if user is already a member
    existing_member = db.session.execute(
        db.select(campaign_members).where(
            and_(
                campaign_members.c.user_id == current_user.id,
                campaign_members.c.campaign_id == campaign.id
            )
        )
    ).first()
    
    if not existing_member:
        # Add user to campaign members
        stmt = campaign_members.insert().values(
            user_id=current_user.id,
            campaign_id=campaign.id
        )
        db.session.execute(stmt)
    
    # Delete the invite
    db.session.delete(invite)
    db.session.commit()
    
    # Send Socket.IO notification to campaign owner
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
    invite = CampaignInvite.query.get_or_404(invite_id)
    
    if invite.invitee_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    if invite.status != 'pending':
        return jsonify({'error': 'Invite already processed'}), 400
    
    # Delete the invite
    db.session.delete(invite)
    db.session.commit()
    
    return jsonify({'message': 'Invite rejected'}), 200

@bp.route('/campaign/<int:campaign_id>', methods=['POST'])
@token_required
def invite_users(current_user, campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Only owner can invite
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Only campaign owner can invite users'}), 403
    
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    
    if not user_ids:
        return jsonify({'error': 'No users specified'}), 400
    
    invited_count = 0
    errors = []
    
    for user_id in user_ids:
        # Check if user exists
        user = User.query.get(user_id)
        if not user:
            errors.append(f'User {user_id} not found')
            continue
        
        # Check if user is already a member
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
        
        # Check if there's already a pending invite
        existing_invite = CampaignInvite.query.filter_by(
            campaign_id=campaign_id,
            invitee_id=user_id,
            status='pending'
        ).first()
        
        if existing_invite:
            errors.append(f'User {user.username} already has a pending invite')
            continue
        
        # Create invite
        invite = CampaignInvite(
            campaign_id=campaign_id,
            inviter_id=current_user.id,
            invitee_id=user_id,
            status='pending'
        )
        db.session.add(invite)
        db.session.flush()  # Get invite ID
        
        # Send Socket.IO notification
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
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Only owner can see available users
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get all users except owner and current members
    member_ids = [m.id for m in campaign.members.all()]
    member_ids.append(campaign.owner_id)
    
    # Get pending invite user IDs
    pending_invites = CampaignInvite.query.filter_by(
        campaign_id=campaign_id,
        status='pending'
    ).all()
    pending_user_ids = [inv.invitee_id for inv in pending_invites]
    
    # Exclude owner, members, and users with pending invites
    exclude_ids = list(set(member_ids + pending_user_ids))
    
    available_users = User.query.filter(
        ~User.id.in_(exclude_ids)
    ).all()
    
    return jsonify([
        {'id': u.id, 'username': u.username, 'email': u.email}
        for u in available_users
    ]), 200
