from app import create_app, socketio

flask_app = create_app()

if __name__ == '__main__':
    with flask_app.app_context():
        # Apply any pending database migrations on startup
        from flask_migrate import upgrade as migrate_upgrade

        try:
            migrate_upgrade()
        except Exception as e:
            print(f"Migration warning: {e}")
            print("Continuing with application startup...")

    socketio.run(flask_app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
