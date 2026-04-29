from flask import Blueprint, request, jsonify
from app import db
from app.models import Notification
from app.jwt.jwt_utils import token_required

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
    
    # Query notifications for current user, sorted by created_at descending
    query = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc())
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    
    # Convert to list of dictionaries
    notifications_list = []
    for notif in pagination.items:
        notifications_list.append({
            'id': notif.id,
            'user_id': notif.user_id,
            'campaign_id': notif.campaign_id,
            'notification_type': notif.notification_type,
            'title': notif.title,
            'message': notif.message,
            'related_post_id': notif.related_post_id,
            'created_at': notif.created_at.isoformat() if notif.created_at else None
        })
    
    return jsonify({
        'notifications': notifications_list,
        'total': pagination.total,
        'page': pagination.page,
        'per_page': per_page,
        'total_pages': pagination.pages
    }), 200

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
    count = Notification.query.filter_by(user_id=current_user.id).count()
    
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
    deleted_count = Notification.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    
    return jsonify({
        'message': 'Notifications deleted',
        'count': deleted_count
    }), 200
