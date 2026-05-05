"""Service for authentication operations."""

from app import db
from app.jwt.jwt_utils import generate_token
from app.models import User


class AuthService:
    """Service for handling authentication business logic."""

    @staticmethod
    def register_user(username, email, password):
        """
        Register a new user.

        Args:
            username (str): Unique username for the user
            email (str): Unique email address
            password (str): User's password (will be hashed)

        Returns:
            tuple: (user, token) or (None, error_message)

        Raises:
            ValueError: If username or email already exists
        """
        if User.query.filter_by(username=username).first():
            raise ValueError('Username already exists')

        if User.query.filter_by(email=email).first():
            raise ValueError('Email already exists')

        user = User(
            username=username,
            email=email
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        token = generate_token(user.id)

        return user, token

    @staticmethod
    def authenticate_user(username, password):
        """
        Authenticate a user and return a JWT token.

        Args:
            username (str): User's username
            password (str): User's password

        Returns:
            tuple: (user, token) or (None, error_message)

        Raises:
            ValueError: If credentials are invalid
        """
        user = User.query.filter_by(username=username).first()

        if not user or not user.check_password(password):
            raise ValueError('Invalid credentials')

        token = generate_token(user.id)

        return user, token
