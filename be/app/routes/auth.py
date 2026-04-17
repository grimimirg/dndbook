from flask import Blueprint, request, jsonify, current_app
from app import db
from app.models import User
from app.auth import generate_token
from app.mock_data import get_mock_user_by_username, MOCK_USERS

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
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
    data = request.get_json()
    
    if not data or not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Missing username or password'}), 400
    
    if current_app.config['MOCK_DATA']:
        mock_user = get_mock_user_by_username(data['username'])
        
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
