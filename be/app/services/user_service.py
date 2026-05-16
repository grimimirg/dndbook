"""Service for user profile operations."""

from app import db
from app.models import User


class UserService:
    """Service for handling user profile business logic."""

    @staticmethod
    def update_profile(user_id, nickname=None, biography=None, avatar_url=None):
        """
        Update user profile information.

        Args:
            user_id (int): The ID of the user to update
            nickname (str, optional): New nickname
            biography (str, optional): New biography
            avatar_url (str, optional): New avatar URL (None to remove avatar)

        Returns:
            User: Updated user object

        Raises:
            ValueError: If user not found
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        if nickname is not None:
            user.nickname = nickname
        if biography is not None:
            user.biography = biography
        # Allow setting avatar_url to None to remove avatar
        user.avatar_url = avatar_url

        db.session.commit()
        return user

    @staticmethod
    def update_password(user_id, current_password, new_password):
        """
        Update user password.

        Args:
            user_id (int): The ID of the user to update
            current_password (str): Current password for verification
            new_password (str): New password

        Returns:
            User: Updated user object

        Raises:
            ValueError: If user not found or current password is incorrect
        """
        user = User.query.get(user_id)
        if not user:
            raise ValueError('User not found')

        if not user.check_password(current_password):
            raise ValueError('Current password is incorrect')

        user.set_password(new_password)
        db.session.commit()
        return user
