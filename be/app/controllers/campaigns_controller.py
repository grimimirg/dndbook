from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import and_

from app import db
from app.controllers.mock_data_controller import MockDataProvider
from app.jwt.jwt_utils import token_required
from app.models import Campaign, CampaignInvite, campaign_members

bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


@bp.route('', methods=['GET'])
@token_required
def get_campaigns(current_user):
    """
    Get all campaigns for the authenticated user.
    
    Returns campaigns owned by the user and campaigns where the user is a member.
    Supports both mock data mode and database queries.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        
    Returns:
        JSON response with:
        - 200: Object containing 'owned' and 'shared' campaign arrays
    """
    if current_app.config['MOCK_DATA']:
        user_id = current_user if isinstance(current_user, int) else current_user.id
        campaigns = MockDataProvider.get_campaigns(user_id)
        return jsonify(campaigns), 200

    owned_campaigns = Campaign.query.filter_by(owner_id=current_user.id).all()

    member_campaigns = [c for c in current_user.member_campaigns if c.owner_id != current_user.id]

    return jsonify({
        'owned': [campaign.to_dict() for campaign in owned_campaigns],
        'shared': [campaign.to_dict() for campaign in member_campaigns]
    }), 200


@bp.route('', methods=['POST'])
@token_required
def create_campaign(current_user):
    """
    Create a new campaign.
    
    Expected JSON payload:
        - name (str): Campaign name (required)
        - description (str): Campaign description (optional)
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        
    Returns:
        JSON response with:
        - 201: Created campaign data
        - 400: Missing campaign name
    """
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
    """
    Get a specific campaign by ID.
    
    User must be either the campaign owner or a member to access.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign to retrieve
        
    Returns:
        JSON response with:
        - 200: Campaign data
        - 403: User is not authorized to access this campaign
        - 404: Campaign not found
    """
    if current_app.config['MOCK_DATA']:
        user_id = current_user if isinstance(current_user, int) else current_user.id
        campaign = MockDataProvider.get_campaign(campaign_id)

        if not campaign or campaign['owner_id'] != user_id:
            return jsonify({'error': 'Unauthorized'}), 403

        return jsonify(campaign), 200

    campaign = Campaign.query.get_or_404(campaign_id)

    is_member = campaign.members.filter_by(id=current_user.id).first() is not None
    if campaign.owner_id != current_user.id and not is_member:
        return jsonify({'error': 'Unauthorized'}), 403

    return jsonify(campaign.to_dict()), 200


@bp.route('/<int:campaign_id>', methods=['PUT'])
@token_required
def update_campaign(current_user, campaign_id):
    """
    Update a campaign.
    
    Only the campaign owner can update the campaign.
    
    Expected JSON payload:
        - name (str): Updated campaign name (optional)
        - description (str): Updated campaign description (optional)
        
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign to update
        
    Returns:
        JSON response with:
        - 200: Updated campaign data
        - 403: User is not the campaign owner
        - 404: Campaign not found
    """
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
    """
    Delete a campaign.
    
    Only the campaign owner can delete the campaign.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign to delete
        
    Returns:
        JSON response with:
        - 200: Success message
        - 403: User is not the campaign owner
        - 404: Campaign not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403

    db.session.delete(campaign)
    db.session.commit()

    return jsonify({'message': 'Campaign deleted successfully'}), 200


@bp.route('/<int:campaign_id>/members', methods=['GET'])
@token_required
def get_campaign_members(current_user, campaign_id):
    """
    Get all members of a campaign and pending invites.
    
    User must be either the campaign owner or a member to access.
    Pending invites are only returned if the user is the campaign owner.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        
    Returns:
        JSON response with:
        - 200: Object containing 'members' array and 'pending_invites' array
        - 403: User is not authorized to access this campaign
        - 404: Campaign not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)

    # Check if user is owner or member
    is_member = campaign.members.filter_by(id=current_user.id).first() is not None
    if campaign.owner_id != current_user.id and not is_member:
        return jsonify({'error': 'Unauthorized'}), 403

    members = [{'id': m.id, 'username': m.username, 'email': m.email} for m in campaign.members.all()]

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
    """
    Remove a member from a campaign.
    
    Only the campaign owner can remove members.
    The campaign owner cannot be removed.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        user_id (int): The ID of the user to remove
        
    Returns:
        JSON response with:
        - 200: Success message
        - 400: Attempted to remove campaign owner
        - 403: User is not the campaign owner
        - 404: Campaign or member not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Only campaign owner can remove members'}), 403

    if user_id == campaign.owner_id:
        return jsonify({'error': 'Cannot remove campaign owner'}), 400

    stmt = db.select(campaign_members).where(
        and_(
            campaign_members.c.user_id == user_id,
            campaign_members.c.campaign_id == campaign_id
        )
    )
    existing_member = db.session.execute(stmt).first()

    if not existing_member:
        return jsonify({'error': 'User is not a member of this campaign'}), 404

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
    """
    Cancel a pending campaign invite.
    
    Only the campaign owner can cancel invites.
    Only pending invites can be cancelled.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        campaign_id (int): The ID of the campaign
        invite_id (int): The ID of the invite to cancel
        
    Returns:
        JSON response with:
        - 200: Success message
        - 400: Invite does not belong to campaign or is not pending
        - 403: User is not the campaign owner
        - 404: Campaign or invite not found
    """
    campaign = Campaign.query.get_or_404(campaign_id)

    if campaign.owner_id != current_user.id:
        return jsonify({'error': 'Only campaign owner can cancel invites'}), 403

    invite = CampaignInvite.query.get_or_404(invite_id)

    if invite.campaign_id != campaign_id:
        return jsonify({'error': 'Invite does not belong to this campaign'}), 400

    if invite.status != 'pending':
        return jsonify({'error': 'Invite is not pending'}), 400

    db.session.delete(invite)
    db.session.commit()

    return jsonify({'message': 'Invite cancelled successfully'}), 200
