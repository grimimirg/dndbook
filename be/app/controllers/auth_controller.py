from flask import Blueprint, request, jsonify, current_app

from app import db
from app.jwt.jwt_utils import generate_token
from app.controllers.mock_data_controller import MockDataProvider
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    
    Expected JSON payload:
        - username (str): Unique username for the user
        - email (str): Unique email address
        - password (str): User's password (will be hashed)
        
    Returns:
        JSON response with:
        - 201: Success with token and user data
        - 400: Missing required fields or validation error
    """
    data = request.get_json()

    if not data or not data.get('username') or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Missing required fields'}), 400

    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists'}), 400

    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email already exists'}), 400

    user = User(
        username=data['username'],
        email=data['email']
    )
    user.set_password(data['password'])

    db.session.add(user)
    db.session.commit()

    token = generate_token(user.id)

    return jsonify({
        'message': 'User created successfully',
        'token': token,
        'user': user.to_dict()
    }), 201


@bp.route('/login', methods=['POST'])
def login():
    """
    Authenticate a user and return a JWT token.
    
    Supports both mock data mode and database authentication.
    
    Expected JSON payload:
        - username (str): User's username
        - password (str): User's password
        
    Returns:
        JSON response with:
        - 200: Success with token and user data
        - 400: Missing username or password
        - 401: Invalid credentials
    """
    data = request.get_json()

    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400

    if current_app.config['MOCK_DATA']:
        mock_user = MockDataProvider.get_user_by_username(data['username'])

        if not mock_user:
            return jsonify({'error': 'Invalid credentials'}), 401

        token = generate_token(mock_user['id'])

        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': mock_user
        }), 200

    user = User.query.filter_by(username=data['username']).first()

    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token(user.id)

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200
