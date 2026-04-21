#!/bin/bash

set -e

echo "==================================="
echo "D&D Book Frontend - Standalone Setup"
echo "==================================="

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file before running the application."
    echo "You can copy .env.example: cp .env.example .env"
    exit 1
fi

echo ""
echo "Checking Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18 or higher required. Current version: $(node --version)"
    exit 1
fi
echo "✓ Node.js $(node --version) found"

echo ""
echo "Checking npm..."
if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm."
    exit 1
fi
echo "✓ npm $(npm --version) found"

echo ""
echo "Installing dependencies..."
npm install
echo "✓ Dependencies installed"

echo ""
echo "==================================="
echo "Starting development server..."
echo "==================================="
echo ""

npm run dev
