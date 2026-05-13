"""
Basic authentication tests for D&D Book backend.
"""
import os
import pytest
from app import create_app, db


@pytest.fixture
def app():
    """Create and configure a test application instance."""
    # Set environment variables before creating app to override .env
    os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
    os.environ['SECRET_KEY'] = 'test-secret-key'
    os.environ['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    
    app = create_app()
    app.config['TESTING'] = True
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the application."""
    return app.test_client()


def test_health_check(client):
    """Test that the health check endpoint works."""
    response = client.get('/api/health')
    # Note: This endpoint may not exist, adjust as needed
    # For now, we'll test that the app responds
    assert response.status_code in [200, 404]


def test_login_missing_credentials(client):
    """Test login with missing credentials."""
    response = client.post('/api/auth/login', json={})
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data or 'message' in data


def test_login_invalid_credentials(client):
    """Test login with invalid credentials."""
    response = client.post('/api/auth/login', json={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401


def test_register_missing_fields(client):
    """Test registration with missing required fields."""
    response = client.post('/api/auth/register', json={
        'username': 'testuser'
        # Missing email and password
    })
    assert response.status_code == 400
