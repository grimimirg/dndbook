"""Service for notification operations."""

from app import db
from app.models import Notification


class NotificationsService:
    """Service for handling notification business logic."""

    @staticmethod
    def get_notifications(user, page=1, per_page=20):
        """
        Get all notifications for a user with pagination.

        Args:
            user: The user to get notifications for
            page (int): Page number (default: 1)
            per_page (int): Items per page (default: 20)

        Returns:
            dict: Object containing notifications list and pagination metadata
        """
        query = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc())
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

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
                'related_comment_id': notif.related_comment_id,
                'created_at': notif.created_at.isoformat() + 'Z' if notif.created_at else None
            })

        return {
            'notifications': notifications_list,
            'total': pagination.total,
            'page': pagination.page,
            'per_page': per_page,
            'total_pages': pagination.pages
        }

    @staticmethod
    def get_unread_count(user):
        """
        Get count of unread notifications for a user.

        Since notifications are deleted when viewed, this returns the total count.

        Args:
            user: The user to get the count for

        Returns:
            int: Count of notifications
        """
        count = Notification.query.filter_by(user_id=user.id).count()
        return count

    @staticmethod
    def delete_notifications(user):
        """
        Delete all notifications for a user.

        This is called when the notification popup opens to prevent table growth.

        Args:
            user: The user to delete notifications for

        Returns:
            int: Number of deleted notifications
        """
        deleted_count = Notification.query.filter_by(user_id=user.id).delete()
        db.session.commit()
        return deleted_count
