from flask import Blueprint, request, jsonify

from app.services.auth_service import AuthService

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

    try:
        user, token = AuthService.register_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        return jsonify({
            'message': 'User created successfully',
            'token': token,
            'user': user.to_dict()
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400


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

    try:
        user, token = AuthService.authenticate_user(
            username=data['username'],
            password=data['password']
        )
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
    except ValueError as e:
        return jsonify({'error': str(e)}), 401
