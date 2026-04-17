#!/bin/bash

set -e

echo "D&D Book - Complete Project Setup"
echo "====================================="
echo ""

command_exists() {
    command -v "$1" &> /dev/null
}

echo "Checking prerequisites..."
echo ""

MISSING_DEPS=false

if ! command_exists uv; then
    echo "❌ uv is not installed"
    MISSING_DEPS=true
else
    echo "uv is installed"
fi

if ! command_exists node; then
    echo "Node.js is not installed"
    MISSING_DEPS=true
else
    echo "Node.js is installed ($(node --version))"
fi

if ! command_exists npm; then
    echo "npm is not installed"
    MISSING_DEPS=true
else
    echo "npm is installed ($(npm --version))"
fi

echo ""

if [ "$MISSING_DEPS" = true ]; then
    echo "Some dependencies are missing. Please install them first:"
    echo ""
    if ! command_exists uv; then
        echo "  • uv: curl -LsSf https://astral.sh/uv/install.sh | sh"
    fi
    if ! command_exists node || ! command_exists npm; then
        echo "  • Node.js & npm: https://nodejs.org/"
    fi
    echo ""
    read -p "Do you want to install uv automatically? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]] && ! command_exists uv; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "⚠️  Please restart your terminal and run this script again."
        exit 0
    else
        exit 1
    fi
fi

# Setup Backend
echo "=================================="
echo "Setting up Backend..."
echo "=================================="
echo ""
cd be
chmod +x setup.sh
./setup.sh
cd ..

echo ""
echo "=================================="
echo "Setting up Frontend..."
echo "=================================="
echo ""
cd fe
chmod +x setup.sh
./setup.sh
cd ..

echo ""
echo "=================================="
echo "✅ Complete Setup Finished!"
echo "=================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure your environment files:"
echo "   • be/.env - Backend configuration"
echo "   • fe/.env - Frontend configuration"
echo ""
echo "2. Start the backend:"
echo "   cd be"
echo "   source .venv/bin/activate"
echo "   python app.py"
echo ""
echo "3. Start the frontend (in a new terminal):"
echo "   cd fe"
echo "   npm run dev"
echo ""
echo "4. Access the application:"
echo "   • Frontend: http://localhost:5173"
echo "   • Backend API: http://localhost:5000"
echo ""
echo "For Docker deployment, see README.md"
echo ""
