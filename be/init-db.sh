#!/bin/bash

set -e

echo "Initializing database..."

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[ERROR] .env file not found"
    echo "Please create .env file first:"
    echo "  cp .env.example .env"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[WARNING] Virtual environment not activated"
    echo "Activating .venv..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo "[ERROR] Virtual environment not found"
        echo "Please create it first:"
        echo "  python3 -m venv .venv"
        exit 1
    fi
fi

# Execute Python code inline without creating temporary files
python << 'EOF'
import sys
import os

# Import from the app package
from app import create_app, db
from app.models import User

# Create the Flask app
flask_app = create_app()

try:
    with flask_app.app_context():
        db.create_all()
        print("\n[SUCCESS] Database tables created successfully!")
        
        # Create default admin user
        admin_password = os.getenv('ADMIN_PASSWORD')
        if not admin_password:
            print("\n[WARNING] ADMIN_PASSWORD not set in .env file, using default 'admin123'")
            admin_password = 'admin123'
        
        # Check if admin user already exists
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@dndbook.local'
            )
            admin_user.set_password(admin_password)
            db.session.add(admin_user)
            db.session.commit()
            print("[SUCCESS] Default admin user created successfully!")
            print(f"  Username: admin")
            print(f"  Email: admin@dndbook.local")
        else:
            print("[INFO] Admin user already exists, skipping creation")
            
except Exception as e:
    print(f"\n[ERROR] Failed to create database tables: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF
RESULT=$?

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "Database initialization complete!"
else
    exit $RESULT
fi
