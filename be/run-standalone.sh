#!/bin/bash

set -e

POSTGRES_CONTAINER="dndbook-postgres"
POSTGRES_VOLUME="dndbook-postgres-data"
POSTGRES_PORT=5432
POSTGRES_USER="dndbook_user"
POSTGRES_PASSWORD="dndbook_password"
POSTGRES_DB="dndbook_db"

echo "==================================="
echo "D&D Book Backend - Standalone Setup"
echo "==================================="

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file before running the application."
    echo "You can copy .env.example: cp .env.example .env"
    exit 1
fi

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
echo "==================================="
echo "Starting application..."
echo "==================================="
echo ""
echo "PostgreSQL: localhost:$POSTGRES_PORT"
echo "Database: $POSTGRES_DB"
echo ""

export FLASK_APP=app.py
python app.py
