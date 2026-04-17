from app import create_app, db, socketio

app = create_app()

# Import socketio events
import app.socketio_events

@app.cli.command()
def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
