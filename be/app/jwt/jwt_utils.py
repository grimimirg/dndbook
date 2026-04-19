import jwt
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from functools import wraps

from app.models import User


def generate_token(user_id):
    """
    Generate a JWT token for a user.
    
    Args:
        user_id: The unique identifier of the user
        
    Returns:
        str: A JWT token valid for 7 days
    """
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return token


def decode_token(token):
    """
    Decode and validate a JWT token.
    
    Args:
        token (str): The JWT token to decode
        
    Returns:
        dict: The decoded payload if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def token_required(f):
    """
    Decorator to protect routes that require authentication.
    
    Validates the JWT token from the Authorization header and injects
    the current_user as the first argument to the decorated function.
    
    Args:
        f: The function to decorate
        
    Returns:
        function: The decorated function that requires a valid token
        
    Usage:
        @token_required
        def protected_route(current_user):
            return jsonify({'user': current_user.username})
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Token is invalid or expired'}), 401

        current_user = User.query.get(payload['user_id'])
        if not current_user:
            return jsonify({'error': 'User not found'}), 401

        return f(current_user, *args, **kwargs)

    return decorated
