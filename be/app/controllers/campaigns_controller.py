from flask import Blueprint, request, jsonify

from app.jwt.jwt_utils import token_required
from app.services.campaigns_service import CampaignsService

bp = Blueprint('campaigns', __name__, url_prefix='/api/campaigns')


@bp.route('', methods=['GET'])
@token_required
def get_campaigns(current_user):
    """
    Get all campaigns for the authenticated user.
    
    Returns campaigns owned by the user and campaigns where the user is a member.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        
    Returns:
        JSON response with:
        - 200: Object containing 'owned' and 'shared' campaign arrays
    """
    result = CampaignsService.get_user_campaigns(current_user)
    return jsonify(result), 200


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

    campaign = CampaignsService.create_campaign(
        user=current_user,
        name=data['name'],
        description=data.get('description', '')
    )

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
    try:
        campaign = CampaignsService.get_campaign(campaign_id, current_user)
        return jsonify(campaign.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403


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
    data = request.get_json()
    try:
        campaign = CampaignsService.update_campaign(
            campaign_id=campaign_id,
            user=current_user,
            name=data.get('name'),
            description=data.get('description')
        )
        return jsonify(campaign.to_dict()), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403


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
    try:
        CampaignsService.delete_campaign(campaign_id, current_user)
        return jsonify({'message': 'Campaign deleted successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403


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
    try:
        result = CampaignsService.get_campaign_members(campaign_id, current_user)
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403


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
    try:
        CampaignsService.remove_campaign_member(campaign_id, user_id, current_user)
        return jsonify({'message': 'Member removed successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'owner' in str(e) else 403


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
    try:
        CampaignsService.cancel_invite(campaign_id, invite_id, current_user)
        return jsonify({'message': 'Invite cancelled successfully'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
