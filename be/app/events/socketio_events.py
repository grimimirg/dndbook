import jwt
from flask import current_app, request
from flask_socketio import emit, join_room, leave_room

from app import socketio

user_sessions = {}


@socketio.on('connect')
def handle_connect(auth):
    """Handle client connection"""
    try:
        # Verify JWT token from auth
        if auth and 'token' in auth:
            token = auth['token']
            decoded = jwt.decode(
                token,
                current_app.config['JWT_SECRET_KEY'],
                algorithms=['HS256']
            )
            user_id = decoded['user_id']

            # Store session
            user_sessions[user_id] = request.sid

            # Join user's personal room
            join_room(f'user_{user_id}')

            return True
        else:
            return False
    except Exception as e:
        print(f'Connection error: {e}')
        return False


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    # Remove from user_sessions
    for user_id, sid in list(user_sessions.items()):
        if sid == request.sid:
            del user_sessions[user_id]
            break


def send_invite_notification(user_id, invite_data):
    """Send invite notification to a specific user"""
    socketio.emit(
        'new_invite',
        invite_data,
        room=f'user_{user_id}'
    )


def send_player_joined_notification(owner_id, player_data):
    """Send notification to campaign owner when a player accepts invite"""
    socketio.emit(
        'player_joined',
        player_data,
        room=f'user_{owner_id}'
    )


def send_notification(user_id):
    """Send notification update to a specific user"""
    socketio.emit(
        'notification_update',
        {},
        room=f'user_{user_id}'
    )
