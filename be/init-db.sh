#!/bin/bash

set -e

echo "==================================="
echo "Database Initialization"
echo "==================================="

# Load environment variables (root first, then backend)
if [ -f "../.env" ]; then
    echo "Loading root .env..."
    export $(grep -v '^#' ../.env | xargs)
fi

if [ -f ".env" ]; then
    echo "Loading backend .env..."
    export $(grep -v '^#' .env | xargs)
fi

# Validate required environment variables
REQUIRED_VARS=("DATABASE_URL" "ADMIN_PASSWORD")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables in .env:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please update your .env file with all required variables."
    exit 1
fi

echo "Checking database connection..."

# Wait for database to be ready (max 30 seconds)
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
except Exception as e:
    sys.exit(1)
" 2>/dev/null; then
        echo "✓ Database connection successful"
        break
    fi
    
    if [ $i -eq 30 ]; then
        echo "❌ Database connection failed after 30 attempts"
        exit 1
    fi
    
    echo "Waiting for database... (attempt $i/30)"
    sleep 1
done

echo ""
echo "Creating database tables..."

python3 << 'PYTHON_SCRIPT'
import os
import sys
from app import create_app, db
from app.models import User, Campaign, Post, CampaignInvite, Character
from werkzeug.security import generate_password_hash

try:
    app = create_app()
    
    with app.app_context():
        # Check if tables already exist
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
            print(f"✓ Admin user created (username: admin, password: {admin_password})")
        
        print("")
        print("===================================")
        print("Database initialization complete!")
        print("===================================")
        
except Exception as e:
    print(f"❌ Error during database initialization: {e}")
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
