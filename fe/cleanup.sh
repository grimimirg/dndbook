#!/bin/bash

set -e

echo "D&D Book Frontend - Cleanup"
echo "==================================="
echo ""

read -p "This will remove node_modules, dist, and .env file. Continue? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled"
    exit 0
fi

echo ""
echo "Removing node_modules..."
if [ -d "node_modules" ]; then
    rm -rf node_modules
    echo "node_modules removed"
else
    echo "No node_modules found"
fi

echo ""
echo "Removing dist directory..."
if [ -d "dist" ]; then
    rm -rf dist
    echo "dist directory removed"
else
    echo "No dist directory found"
fi

echo ""
echo "Cleanup complete!"
echo ""
echo "To set up the frontend again, run:"
echo "  ./setup.sh"
echo ""
