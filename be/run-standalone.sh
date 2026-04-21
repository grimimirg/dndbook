#!/bin/bash

set -e

echo "==================================="
echo "D&D Book Backend - Standalone Setup"
echo "==================================="

echo ""
echo "Loading environment variables..."

# Load root .env first (shared configuration)
if [ -f "../.env" ]; then
    echo "  ✓ Loading ../env (shared configuration)"
    export $(grep -v '^#' ../.env | xargs)
else
    echo "  ⚠️  Root .env not found, using only backend .env"
fi

# Load backend .env (can override root values)
if [ -f ".env" ]; then
    echo "  ✓ Loading be/.env (backend-specific configuration)"
    export $(grep -v '^#' .env | xargs)
else
    echo "  ℹ️  Backend .env not found, using only root configuration"
fi

# Validate required environment variables
REQUIRED_VARS=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB" "POSTGRES_HOST" "POSTGRES_PORT" "DATABASE_URL" "SECRET_KEY" "JWT_SECRET_KEY" "ADMIN_PASSWORD")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo ""
    echo "❌ Missing required environment variables:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "These variables must be defined in either:"
    echo "  - Root .env (../.env) for shared configuration, OR"
    echo "  - Backend .env (be/.env) for backend-specific values"
    echo ""
    echo "See .env.example files for reference."
    exit 1
fi

# Set PostgreSQL container configuration
POSTGRES_CONTAINER="dndbook-postgres"
POSTGRES_VOLUME="dndbook-postgres-data"

echo "✓ Environment variables loaded and validated"

echo ""
echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker for PostgreSQL."
    exit 1
fi
echo "✓ Docker found"

echo ""
echo "Checking Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION found"

echo ""
echo "Checking system dependencies for PostgreSQL..."
if ! dpkg -l | grep -q libpq-dev 2>/dev/null && ! rpm -q postgresql-devel &>/dev/null; then
    echo "⚠️  libpq-dev might not be installed."
    echo "On Debian/Ubuntu: sudo apt-get install libpq-dev python3-dev"
    echo "On RHEL/Fedora: sudo dnf install postgresql-devel python3-devel"
fi

echo ""
echo "Creating virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

echo ""
echo "Activating virtual environment..."
source venv/bin/activate

echo ""
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Dependencies installed"

echo ""
echo "Setting up PostgreSQL container..."
if docker ps -a -q -f name=$POSTGRES_CONTAINER | grep -q .; then
    if docker ps -q -f name=$POSTGRES_CONTAINER | grep -q .; then
        echo "✓ PostgreSQL container already running"
    else
        echo "Starting existing PostgreSQL container..."
        docker start $POSTGRES_CONTAINER
        echo "✓ PostgreSQL container started"
    fi
else
    echo "Creating PostgreSQL container..."
    docker run -d \
        --name $POSTGRES_CONTAINER \
        -e POSTGRES_USER=$POSTGRES_USER \
        -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
        -e POSTGRES_DB=$POSTGRES_DB \
        -p $POSTGRES_PORT:5432 \
        -v $POSTGRES_VOLUME:/var/lib/postgresql/data \
        postgres:15-alpine
    echo "✓ PostgreSQL container created and started"
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 5
fi

echo ""
echo "Creating uploads directory..."
mkdir -p uploads
chmod 755 uploads
echo "✓ Uploads directory ready"

echo ""
echo "Initializing database..."
if [ -f "init-db.sh" ]; then
    ./init-db.sh
    if [ $? -ne 0 ]; then
        echo "❌ Database initialization failed"
        exit 1
    fi
else
    echo "⚠️  init-db.sh not found, skipping database initialization"
fi

echo ""
echo "==================================="
echo "Starting application..."
echo "==================================="
echo ""
echo "PostgreSQL: localhost:$POSTGRES_PORT"
echo "Database: $POSTGRES_DB"
echo ""

echo "Database URL: $DATABASE_URL"
echo ""

export FLASK_APP=main.py
python main.py
