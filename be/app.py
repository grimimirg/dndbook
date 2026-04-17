from app import create_app, db, socketio

flask_app = create_app()

# Import socketio events
import app.socketio_events

if __name__ == '__main__':
    socketio.run(flask_app, host='0.0.0.0', port=5000, debug=True)
