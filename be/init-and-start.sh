#!/bin/bash

set -e

echo "==================================="
echo "D&D Book Backend - Starting"
echo "==================================="

# Validate required environment variables
REQUIRED_VARS=("DATABASE_URL" "SECRET_KEY" "JWT_SECRET_KEY" "ADMIN_PASSWORD")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "These variables must be set in the environment or .env file."
    exit 1
fi

# Wait for database to be ready
echo "Waiting for database to be ready..."

MAX_RETRIES=30
RETRY_COUNT=0

until python3 -c "
import os
from sqlalchemy import create_engine
try:
    engine = create_engine(os.getenv('DATABASE_URL'))
    conn = engine.connect()
    conn.close()
    exit(0)
except Exception:
    exit(1)
" 2>/dev/null; do
    RETRY_COUNT=$((RETRY_COUNT + 1))
    
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "❌ Database connection failed after $MAX_RETRIES attempts"
        exit 1
    fi
    
    echo "Database not ready yet... (attempt $RETRY_COUNT/$MAX_RETRIES)"
    sleep 2
done

echo "✓ Database connection successful"

# Initialize database
echo ""
echo "Initializing database..."

python3 << 'PYTHON_SCRIPT'
import os
import sys
from app import create_app, db
from app.models import User, Campaign, Post, CampaignInvite, Character
from werkzeug.security import generate_password_hash

try:
    app = create_app()
    
    with app.app_context():
        # Check if tables exist
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        if existing_tables:
            print(f"✓ Database tables already exist: {', '.join(existing_tables)}")
        else:
            # Create all tables
            db.create_all()
            print("✓ Database tables created successfully")
        
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
            print(f"✓ Admin user created (username: admin)")
        
        print("✓ Database initialization complete")
        
except Exception as e:
    print(f"❌ Error during database initialization: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

PYTHON_SCRIPT

if [ $? -ne 0 ]; then
    echo "❌ Database initialization failed"
    exit 1
fi

echo ""
echo "==================================="
echo "Starting Flask application..."
echo "==================================="
echo ""

# Start the application
exec python3 main.py
