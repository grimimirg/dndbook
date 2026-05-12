import eventlet

eventlet.monkey_patch()

from app import create_app, socketio, db, migrate

flask_app = create_app()

if __name__ == '__main__':
    with flask_app.app_context():
        # Auto-upgrade database on startup
        from flask_migrate import upgrade as migrate_upgrade
        try:
            migrate_upgrade()
        except Exception as e:
            print(f"Migration failed: {e}")
            print("Continuing anyway...")
    
    socketio.run(flask_app, host='0.0.0.0', port=5000, debug=False)
