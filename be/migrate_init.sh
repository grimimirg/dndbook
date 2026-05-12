#!/bin/bash

# Script to initialize Flask-Migrate and generate initial migration
# Run this once after setting up the project

set -e

echo "======================================"
echo "Initializing Flask-Migrate"
echo "======================================"

# Load environment variables
if [ -f "../.env" ]; then
    set -a
    source ../.env
    set +a
elif [ -f ".env" ]; then
    set -a
    source .env
    set +a
else
    echo "❌ .env file not found"
    exit 1
fi

echo "✓ Environment variables loaded"

# Initialize Flask-Migrate
echo ""
echo "Initializing Flask-Migrate..."
flask db init

echo "✓ Flask-Migrate initialized"

# Generate initial migration
echo ""
echo "Generating initial migration..."
flask db migrate -m "Initial migration"

echo "✓ Initial migration generated"

echo ""
echo "======================================"
echo "Flask-Migrate setup complete!"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Review the generated migration in migrations/versions/"
echo "2. Apply the migration: flask db upgrade"
echo "3. For future schema changes, use: flask db migrate -m 'description'"
echo "4. Then apply with: flask db upgrade"
