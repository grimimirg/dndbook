#!/bin/bash

set -e

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

echo "==================================="
echo "Database Initialization"
echo "==================================="

# Load environment variables
# 1. Load root .env first (shared configuration)
if [ -f "$ROOT_DIR/.env" ]; then
    echo "Loading $ROOT_DIR/.env..."
    set -a
    source "$ROOT_DIR/.env"
    set +a
fi

# 2. Load backend .env second (can override root values)
if [ -f "$SCRIPT_DIR/.env" ]; then
    echo "Loading $SCRIPT_DIR/.env..."
    set -a
    source "$SCRIPT_DIR/.env"
    set +a
fi

# Build DATABASE_URL from components if not set
if [ -z "$DATABASE_URL" ] && [ -n "$POSTGRES_USER" ] && [ -n "$POSTGRES_PASSWORD" ] && [ -n "$POSTGRES_DB" ]; then
    POSTGRES_HOST="${POSTGRES_HOST:-localhost}"
    POSTGRES_PORT="${POSTGRES_PORT:-5432}"
    DATABASE_URL="postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
    echo "Constructed DATABASE_URL from components"
fi

# Validate required environment variables
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL not set"
    echo "Please set DATABASE_URL in $ROOT_DIR/.env or $SCRIPT_DIR/.env"
    exit 1
fi

if [ -z "$ADMIN_PASSWORD" ]; then
    echo "❌ ADMIN_PASSWORD not set"
    echo "Please set ADMIN_PASSWORD in $ROOT_DIR/.env or $SCRIPT_DIR/.env"
    exit 1
fi

echo "✓ Environment variables loaded"
echo "  DATABASE_URL: ${DATABASE_URL//:*@***:****}"  # Hide password

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "Activating virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Check if postgres container is running (standalone mode)
if command -v docker &> /dev/null; then
    if docker ps -q -f name=dndbook-postgres | grep -q .; then
        echo "✓ PostgreSQL container is running"
    elif docker ps -a -q -f name=dndbook-postgres | grep -q .; then
        echo "Starting PostgreSQL container..."
        docker start dndbook-postgres
        echo "⏳ Waiting for PostgreSQL to be ready..."
        sleep 3
    else
        echo "⚠️  PostgreSQL container not found (assuming external database)"
    fi
fi

# Wait for database to be ready (max 30 seconds)
echo "Checking database connection..."
for i in {1..30}; do
    if python3 -c "
import os
import sys
from sqlalchemy import create_engine
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    conn = engine.connect()
    conn.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
" 2>/dev/null; then
        echo "✓ Database connection successful"
        break
    fi

    if [ $i -eq 30 ]; then
        echo "❌ Database connection failed after 30 attempts"
        echo "Please check:"
        echo "  - PostgreSQL container is running"
        echo "  - DATABASE_URL is correct"
        echo "  - Environment variables are set"
        exit 1
    fi

    echo "Waiting for database... (attempt $i/30)"
    sleep 1
done

# Initialize database
echo ""
echo "Initializing database..."

python3 << 'PYTHON_SCRIPT'
import os
import sys
from app import create_app, db
from app.models import User, Campaign, Post, CampaignInvite, Character, PostViewedStatus, Notification
from werkzeug.security import generate_password_hash

try:
    app = create_app()
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created/updated")
        
        # Check if admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            print("✓ Admin user already exists")
        else:
            # Create admin user
            admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
            admin = User(
                username='admin',
                email='admin@dndbook.local',
                password_hash=generate_password_hash(admin_password)
            )
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin user created (username: admin, password: {admin_password})")
        
        print("")
        print("===================================")
        print("Database initialization complete!")
        print("===================================")
        
except Exception as e:
    print(f"❌ Error during database initialization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

PYTHON_SCRIPT

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Database is ready!"
    exit 0
else
    echo ""
    echo "❌ Database initialization failed"
    exit 1
fi
