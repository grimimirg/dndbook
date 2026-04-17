#!/bin/bash

set -e

echo "Starting D&D Book Backend..."

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
until python -c "
import psycopg2
import os
import sys
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print('[ERROR] DATABASE_URL not set')
    sys.exit(1)

parsed = urlparse(db_url)
try:
    conn = psycopg2.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        database=parsed.path[1:],
        connect_timeout=3
    )
    conn.close()
    print('[SUCCESS] PostgreSQL is ready')
except Exception as e:
    print(f'[WAITING] PostgreSQL not ready yet: {e}')
    sys.exit(1)
" 2>/dev/null; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done

# Check if database is initialized
echo "Checking database initialization..."
DB_INITIALIZED=$(python -c "
import os
import sys
from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    try:
        # Try to query users table
        User.query.first()
        print('true')
    except Exception:
        print('false')
" 2>/dev/null || echo "false")

if [ "$DB_INITIALIZED" = "false" ]; then
    echo "[INFO] Database not initialized, running initialization..."
    ./init-db.sh
else
    echo "[INFO] Database already initialized, skipping..."
fi

echo "Starting Flask application..."
exec python app.py
