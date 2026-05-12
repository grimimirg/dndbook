"""
Unit tests for AuthService using GIVEN-WHEN-THEN pattern.
"""
import pytest
from app.services.auth_service import AuthService
from app.models import User


def test_register_user_success(app):
    """GIVEN a new user registration request
    WHEN registering the user
    THEN the user should be created with valid credentials and token
    """
    with app.app_context():
        # GIVEN
        username = 'testuser'
        email = 'test@example.com'
        password = 'password123'
        
        # WHEN
        user, token = AuthService.register_user(
            username=username,
            email=email,
            password=password
        )
        
        # THEN
        assert user is not None
        assert user.username == username
        assert user.email == email
        assert token is not None
        assert user.check_password(password)


def test_register_user_duplicate_username(app):
    """GIVEN an existing user with a specific username
    WHEN attempting to register a new user with the same username
    THEN registration should fail with 'Username already exists' error
    """
    with app.app_context():
        # GIVEN
        username = 'testuser'
        AuthService.register_user(
            username=username,
            email='test1@example.com',
            password='password123'
        )
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Username already exists'):
            AuthService.register_user(
                username=username,
                email='test2@example.com',
                password='password456'
            )


def test_register_user_duplicate_email(app):
    """GIVEN an existing user with a specific email
    WHEN attempting to register a new user with the same email
    THEN registration should fail with 'Email already exists' error
    """
    with app.app_context():
        # GIVEN
        email = 'test@example.com'
        AuthService.register_user(
            username='testuser1',
            email=email,
            password='password123'
        )
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Email already exists'):
            AuthService.register_user(
                username='testuser2',
                email=email,
                password='password456'
            )


def test_authenticate_user_success(app):
    """GIVEN a registered user
    WHEN authenticating with correct credentials
    THEN authentication should succeed and return user and token
    """
    with app.app_context():
        # GIVEN
        username = 'testuser'
        password = 'password123'
        AuthService.register_user(
            username=username,
            email='test@example.com',
            password=password
        )
        
        # WHEN
        user, token = AuthService.authenticate_user(
            username=username,
            password=password
        )
        
        # THEN
        assert user is not None
        assert user.username == username
        assert token is not None


def test_authenticate_user_invalid_username(app):
    """GIVEN a non-existent username
    WHEN attempting to authenticate
    THEN authentication should fail with 'Invalid credentials' error
    """
    with app.app_context():
        # GIVEN
        username = 'nonexistent'
        password = 'password123'
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Invalid credentials'):
            AuthService.authenticate_user(
                username=username,
                password=password
            )


def test_authenticate_user_invalid_password(app):
    """GIVEN a registered user
    WHEN attempting to authenticate with wrong password
    THEN authentication should fail with 'Invalid credentials' error
    """
    with app.app_context():
        # GIVEN
        username = 'testuser'
        AuthService.register_user(
            username=username,
            email='test@example.com',
            password='password123'
        )
        
        # WHEN & THEN
        with pytest.raises(ValueError, match='Invalid credentials'):
            AuthService.authenticate_user(
                username=username,
                password='wrongpassword'
            )
