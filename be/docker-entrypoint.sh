# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
echo "DATABASE_URL: $DATABASE_URL"
until python -c "
import psycopg2
import os
import sys
from urllib.parse import urlparse

db_url = os.getenv('DATABASE_URL')
if not db_url:
    print('[ERROR] DATABASE_URL not set')
    sys.exit(1)

print(f'[DEBUG] Connecting to: {db_url}')
parsed = urlparse(db_url)
print(f'[DEBUG] Host: {parsed.hostname}')
print(f'[DEBUG] Port: {parsed.port or 5432}')
print(f'[DEBUG] User: {parsed.username}')
print(f'[DEBUG] Database: {parsed.path[1:]}')

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
"; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 2
done