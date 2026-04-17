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

# Initialize database using Python
python << 'EOF'
from app import app, db

try:
    with app.app_context():
        db.create_all()
        print("\n[SUCCESS] Database tables created successfully!")
except Exception as e:
    print(f"\n[ERROR] Failed to create database tables: {e}")
    exit(1)
EOF

echo ""
echo "Database initialization complete!"
