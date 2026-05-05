from flask import Blueprint, request, jsonify

from app.jwt.jwt_utils import token_required
from app.services.invites_service import InvitesService

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
    invites = InvitesService.get_pending_invites(current_user)
    return jsonify(invites), 200


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
    try:
        campaign = InvitesService.accept_invite(invite_id, current_user)
        return jsonify({
            'message': 'Invite accepted',
            'campaign': campaign.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'processed' in str(e) else 403


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
    try:
        InvitesService.reject_invite(invite_id, current_user)
        return jsonify({'message': 'Invite rejected'}), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'processed' in str(e) else 403


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
    data = request.get_json()
    user_ids = data.get('user_ids', [])
    
    try:
        result = InvitesService.invite_users(campaign_id, user_ids, current_user)
        return jsonify({
            'message': f"{result['invited_count']} invite(s) sent",
            'invited_count': result['invited_count'],
            'errors': result['errors']
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 400 if 'users' in str(e) else 403


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
    try:
        available_users = InvitesService.get_available_users(campaign_id, current_user)
        return jsonify(available_users), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 403
