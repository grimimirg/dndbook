#!/bin/bash

set -e

echo "D&D Book Backend - Cleanup"
echo "=================================="
echo ""

read -p "This will remove virtual environment, uploads, and .env file. Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Removing virtual environment..."
if [ -d ".venv" ]; then
    rm -rf .venv
    echo "Virtual environment removed"
else
    echo "No virtual environment found"
fi

echo ""
echo "Removing uploads directory..."
if [ -d "uploads" ]; then
    sudo rm -rf uploads
    echo "Uploads directory removed"
else
    echo "No uploads directory found"
fi

echo ""
echo "Removing __pycache__ directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "Cache directories removed"

echo ""
echo "Cleanup complete!"
echo ""
echo "To set up the backend again, run:"
echo "  ./setup.sh"
echo ""
