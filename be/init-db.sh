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

# Create temporary Python script in the current directory
cat > init_db_temp.py << 'EOF'
import sys

# Import from the app package
from app import create_app, db

# Create the Flask app
flask_app = create_app()

try:
    with flask_app.app_context():
        db.create_all()
        print("\n[SUCCESS] Database tables created successfully!")
except Exception as e:
    print(f"\n[ERROR] Failed to create database tables: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

# Execute the temporary script
python init_db_temp.py
RESULT=$?

# Clean up
rm -f init_db_temp.py

if [ $RESULT -eq 0 ]; then
    echo ""
    echo "Database initialization complete!"
else
    exit $RESULT
fi
