#!/bin/bash

set -e

echo "D&D Book Backend - Quick Setup"
echo "=================================="
echo ""

if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    echo "uv installed successfully"
    echo ""
    echo "⚠Please restart your terminal and run this script again."
    exit 0
fi

echo "Creating virtual environment..."
uv venv

echo ""
echo "Installing dependencies..."
source .venv/bin/activate
uv pip install .

echo ""
echo "⚙Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo "Please edit .env with your configuration"
else
    echo ".env file already exists, skipping..."
fi

echo ""
echo "Database setup..."
read -p "Do you want to initialize the database now? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if grep -q "MOCK_DATA=true" .env; then
        echo "ℹMock data mode is enabled, skipping database initialization"
    else
        flask --app run init-db
        echo "Database initialized"
    fi
else
    echo "Skipping database initialization"
fi

echo ""
echo "Setup complete!"
echo ""
echo "To start the development server:"
echo "  source .venv/bin/activate"
echo "  python app.py"
echo ""
