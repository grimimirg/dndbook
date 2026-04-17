from app import create_app, db

app = create_app()

@app.cli.command()
def init_db():
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
