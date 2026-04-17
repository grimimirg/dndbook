#!/bin/bash

set -e

echo "D&D Book Frontend - Quick Setup"
echo "==================================="
echo ""

if ! command -v npm &> /dev/null; then
    echo "npm is not installed. Please install Node.js and npm first."
    echo "Visit: https://nodejs.org/"
    exit 1
fi

echo "Node.js version: $(node --version)"
echo "npm version: $(npm --version)"
echo ""

echo "⚙Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file from .env.example"
    echo "Please edit .env if needed"
else
    echo ".env file already exists, skipping..."
fi

echo ""
echo "Installing dependencies..."
npm install

echo ""
echo "Setup complete!"
echo ""
echo "To start the development server:"
echo "  npm run dev"
echo ""
echo "The frontend will be available at: http://localhost:5173"
echo ""
