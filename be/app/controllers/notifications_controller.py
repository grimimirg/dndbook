from flask import Blueprint, request, jsonify

from app.jwt.jwt_utils import token_required
from app.services.notifications_service import NotificationsService

bp = Blueprint('notifications', __name__, url_prefix='/api')

@bp.route('/notifications', methods=['GET'])
@token_required
def get_notifications(current_user):
    """
    Get all notifications for the current user with pagination.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        
    Query params:
        page (int): Page number (default: 1)
        per_page (int): Items per page (default: 20)
        
    Returns:
        JSON response with:
        - 200: Paginated list of notifications
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    result = NotificationsService.get_notifications(current_user, page, per_page)
    return jsonify(result), 200

@bp.route('/notifications/unread', methods=['GET'])
@token_required
def get_unread_count(current_user):
    """
    Get count of unread notifications for the current user.
    
    Since notifications are deleted when viewed, this returns the total count.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        
    Returns:
        JSON response with:
        - 200: Count of notifications
    """
    count = NotificationsService.get_unread_count(current_user)
    return jsonify({'count': count}), 200

@bp.route('/notifications', methods=['DELETE'])
@token_required
def delete_notifications(current_user):
    """
    Delete all notifications for the current user.
    
    This is called when the notification popup opens to prevent table growth.
    
    Args:
        current_user: The authenticated user (injected by token_required decorator)
        
    Returns:
        JSON response with:
        - 200: Success message with count deleted
    """
    deleted_count = NotificationsService.delete_notifications(current_user)
    return jsonify({
        'message': 'Notifications deleted',
        'count': deleted_count
    }), 200
