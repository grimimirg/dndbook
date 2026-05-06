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

# PostgreSQL container name (for standalone mode)
POSTGRES_CONTAINER_NAME="${POSTGRES_CONTAINER_NAME}"

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
echo "  DATABASE_URL: ${DATABASE_URL}"
echo "  Connection parameters:"
echo "    POSTGRES_HOST: ${POSTGRES_HOST}"
echo "    POSTGRES_PORT: ${POSTGRES_PORT}"
echo "    POSTGRES_USER: ${POSTGRES_USER}"
echo "    POSTGRES_DB: ${POSTGRES_DB}"
echo "    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}"
echo "    POSTGRES_CONTAINER_NAME: ${POSTGRES_CONTAINER_NAME}"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    echo "Activating virtual environment..."
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Check if postgres container is running (standalone mode)
if command -v docker &> /dev/null; then
    if docker ps -q -f name="$POSTGRES_CONTAINER_NAME" | grep -q .; then
        echo "✓ PostgreSQL container is running"
    elif docker ps -a -q -f name="$POSTGRES_CONTAINER_NAME" | grep -q .; then
        echo "Starting PostgreSQL container..."
        docker start "$POSTGRES_CONTAINER_NAME"
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
from sqlalchemy import inspect, text

try:
    app = create_app()

    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database tables created/updated")

        # Add related_comment_id column to notifications table if it doesn't exist
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('notifications')]

        if 'related_comment_id' not in columns:
            print("Adding related_comment_id column to notifications table...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE notifications ADD COLUMN related_comment_id INTEGER REFERENCES comments(id)"))
                conn.commit()
            print("✓ related_comment_id column added")
        else:
            print("✓ related_comment_id column already exists")

        # Add post_order column to posts table if it doesn't exist
        posts_columns = [col['name'] for col in inspector.get_columns('posts')]

        if 'post_order' not in posts_columns:
            print("Adding post_order column to posts table...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE posts ADD COLUMN post_order INTEGER"))
                conn.execute(text("CREATE INDEX ix_posts_post_order ON posts(post_order)"))
                conn.commit()
            print("✓ post_order column added to posts table")

            # Backfill existing posts with order based on created_at
            print("Backfilling post_order values for existing posts...")
            with db.engine.connect() as conn:
                # Get all campaigns
                campaigns = conn.execute(text("SELECT id FROM campaigns ORDER BY id")).fetchall()
                
                for campaign in campaigns:
                    campaign_id = campaign[0]
                    # Get posts ordered by created_at
                    posts = conn.execute(
                        text("SELECT id FROM posts WHERE campaign_id = :campaign_id ORDER BY created_at"),
                        {'campaign_id': campaign_id}
                    ).fetchall()
                    
                    # Assign sequential order values
                    for idx, post in enumerate(posts, start=1):
                        conn.execute(
                            text("UPDATE posts SET post_order = :order_val WHERE id = :post_id"),
                            {'order_val': idx, 'post_id': post[0]}
                        )
                
                conn.commit()
            print("✓ post_order values backfilled for existing posts")
        else:
            print("✓ post_order column already exists in posts table")

        # Add importance_level column to posts table if it doesn't exist
        if 'importance_level' not in posts_columns:
            print("Adding importance_level column to posts table...")
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE posts ADD COLUMN importance_level INTEGER DEFAULT 0"))
                conn.commit()
            print("✓ importance_level column added to posts table")
        else:
            print("✓ importance_level column already exists in posts table")

        # Add description and order_index columns to images table if they don't exist
        # First check if the table exists
        inspector = inspect(db.engine)
        table_names = inspector.get_table_names()

        if 'images' in table_names:
            images_columns = [col['name'] for col in inspector.get_columns('images')]

            if 'description' not in images_columns:
                print("Adding description column to images table...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE images ADD COLUMN description TEXT"))
                    conn.commit()
                print("✓ description column added to images table")
            else:
                print("✓ description column already exists in images table")

            if 'order_index' not in images_columns:
                print("Adding order_index column to images table...")
                with db.engine.connect() as conn:
                    conn.execute(text("ALTER TABLE images ADD COLUMN order_index INTEGER DEFAULT 0"))
                    conn.commit()
                print("✓ order_index column added to images table")
            else:
                print("✓ order_index column already exists in images table")
        else:
            print("✓ images table does not exist yet (will be created by ORM)")

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
