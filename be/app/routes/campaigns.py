from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import Campaign, CampaignInvite, campaign_members
from app.auth import token_required
from app.mock_data import MockDataProvider
from sqlalchemy import and_

bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')

@bp.route('', methods=['GET'])
@token_required
def get_campaigns(current_user):
    if current_app.config['MOCK_DATA']:
        user_id = current_user if isinstance(current_user, int) else current_user.id
        campaigns = MockDataProvider.get_campaigns(user_id)
        return jsonify(campaigns), 200
    
    # Get owned campaigns
    owned_campaigns = Campaign.query.filter_by(owner_id=current_user.id).all()
    
    # Get member campaigns (campaigns where user is a member but not owner)
    member_campaigns = [c for c in current_user.member_campaigns if c.owner_id != current_user.id]
    
    return jsonify({
        'owned': [campaign.to_dict() for campaign in owned_campaigns],
        'shared': [campaign.to_dict() for campaign in member_campaigns]
    }), 200

@bp.route('', methods=['POST'])
@token_required
def create_campaign(current_user):
    data = request.get_json()
    
    if not data or not data.get('name'):
        return jsonify({'error': 'Campaign name is required'}), 400
    
    campaign = Campaign(
        name=data['name'],
        description=data.get('description', ''),
        owner_id=current_user.id
    )
    
    db.session.add(campaign)
    db.session.commit()
    
    return jsonify(campaign.to_dict()), 201

@bp.route('/<int:campaign_id>', methods=['GET'])
@token_required
def get_campaign(current_user, campaign_id):
    if current_app.config['MOCK_DATA']:
        user_id = current_user if isinstance(current_user, int) else current_user.id
        campaign = MockDataProvider.get_campaign(campaign_id)
        
        if not campaign or campaign['owner_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify(campaign), 200
    
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Check if user is owner or member
    is_member = campaign.members.filter_by(id=current_user.id).first() is not None
    if campaign.owner_id != current_user.id and not is_member:
        return jsonify({'error': 'Unauthorized'}), 403
    
    return jsonify(campaign.to_dict()), 200

@bp.route('/<int:campaign_id>', methods=['PUT'])
@token_required
def update_campaign(current_user, campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json()
    
    if data.get('name'):
        campaign.name = data['name']
    if 'description' in data:
        campaign.description = data['description']
    
    db.session.commit()
    
    return jsonify(campaign.to_dict()), 200

@bp.route('/<int:campaign_id>', methods=['DELETE'])
@token_required
def delete_campaign(current_user, campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(campaign)
    db.session.commit()
    
    return jsonify({'message': 'Campaign deleted successfully'}), 200

@bp.route('/<int:campaign_id>/members', methods=['GET'])
@token_required
def get_campaign_members(current_user, campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Check if user is owner or member
    is_member = campaign.members.filter_by(id=current_user.id).first() is not None
    if campaign.owner_id != current_user.id and not is_member:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Get campaign members
    members = [{'id': m.id, 'username': m.username, 'email': m.email} for m in campaign.members.all()]
    
    # Get pending invites (only if user is owner)
    pending_invites = []
    if campaign.owner_id == current_user.id:
        invites = CampaignInvite.query.filter_by(
            campaign_id=campaign_id,
            status='pending'
        ).all()
        pending_invites = [invite.to_dict() for invite in invites]
    
    return jsonify({
        'members': members,
        'pending_invites': pending_invites
    }), 200

@bp.route('/<int:campaign_id>/members/<int:user_id>', methods=['DELETE'])
@token_required
def remove_campaign_member(current_user, campaign_id, user_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Only owner can remove members
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Only campaign owner can remove members'}), 403
    
    # Cannot remove owner
    if user_id == campaign.owner_id:
        return jsonify({'error': 'Cannot remove campaign owner'}), 400
    
    # Check if user is a member
    stmt = db.select(campaign_members).where(
        and_(
            campaign_members.c.user_id == user_id,
            campaign_members.c.campaign_id == campaign_id
        )
    )
    existing_member = db.session.execute(stmt).first()
    
    if not existing_member:
        return jsonify({'error': 'User is not a member of this campaign'}), 404
    
    # Remove member
    delete_stmt = campaign_members.delete().where(
        and_(
            campaign_members.c.user_id == user_id,
            campaign_members.c.campaign_id == campaign_id
        )
    )
    db.session.execute(delete_stmt)
    db.session.commit()
    
    return jsonify({'message': 'Member removed successfully'}), 200

@bp.route('/<int:campaign_id>/invites/<int:invite_id>', methods=['DELETE'])
@token_required
def cancel_invite(current_user, campaign_id, invite_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    
    # Only owner can cancel invites
    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Only campaign owner can cancel invites'}), 403
    
    invite = CampaignInvite.query.get_or_404(invite_id)
    
    # Verify invite belongs to this campaign
    if invite.campaign_id != campaign_id:
        return jsonify({'error': 'Invite does not belong to this campaign'}), 400
    
    if invite.status != 'pending':
        return jsonify({'error': 'Invite is not pending'}), 400
    
    db.session.delete(invite)
    db.session.commit()
    
    return jsonify({'message': 'Invite cancelled successfully'}), 200
