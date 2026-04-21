#!/bin/bash

set -e

POSTGRES_CONTAINER="dndbook-postgres"
POSTGRES_VOLUME="dndbook-postgres-data"

echo "==================================="
echo "D&D Book Backend - Standalone Cleanup"
echo "==================================="

echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi
echo "✓ Docker found"

echo ""
echo "Stopping PostgreSQL container (if running)..."
if docker ps -q -f name=$POSTGRES_CONTAINER | grep -q .; then
    docker stop $POSTGRES_CONTAINER
    echo "✓ Container stopped"
else
    echo "ℹ️  Container not running"
fi

echo ""
echo "Removing PostgreSQL container..."
if docker ps -a -q -f name=$POSTGRES_CONTAINER | grep -q .; then
    docker rm $POSTGRES_CONTAINER
    echo "✓ Container removed"
else
    echo "ℹ️  Container does not exist"
fi

echo ""
read -p "Do you want to remove the PostgreSQL volume (database data will be lost)? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if docker volume ls -q -f name=$POSTGRES_VOLUME | grep -q .; then
        docker volume rm $POSTGRES_VOLUME
        echo "✓ Volume removed"
    else
        echo "ℹ️  Volume does not exist"
    fi
else
    echo "ℹ️  Volume kept (database data preserved)"
fi

echo ""
echo "Removing virtual environment..."
if [ -d "venv" ]; then
    rm -rf venv
    echo "✓ Virtual environment removed"
else
    echo "ℹ️  Virtual environment does not exist"
fi

echo ""
echo "==================================="
echo "Cleanup complete!"
echo "==================================="
