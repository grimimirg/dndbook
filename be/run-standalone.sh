#!/bin/bash

set -e

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
echo "Creating uploads directory..."
mkdir -p uploads
chmod 755 uploads
echo "✓ Uploads directory ready"

echo ""
echo "==================================="
echo "Starting application..."
echo "==================================="
echo ""

export FLASK_APP=app.py
python app.py
