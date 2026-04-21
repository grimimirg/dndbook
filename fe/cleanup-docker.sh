#!/bin/bash

set -e

IMAGE_NAME="dndbook-frontend"
CONTAINER_NAME="dndbook-frontend"

echo "==================================="
echo "D&D Book Frontend - Docker Cleanup"
echo "==================================="

echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi
echo "✓ Docker found"

echo ""
echo "Stopping container (if running)..."
if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
    docker stop $CONTAINER_NAME
    echo "✓ Container stopped"
else
    echo "ℹ️  Container not running"
fi

echo ""
echo "Removing container..."
if docker ps -a -q -f name=$CONTAINER_NAME | grep -q .; then
    docker rm $CONTAINER_NAME
    echo "✓ Container removed"
else
    echo "ℹ️  Container does not exist"
fi

echo ""
echo "Removing image..."
if docker images -q $IMAGE_NAME | grep -q .; then
    docker rmi $IMAGE_NAME
    echo "✓ Image removed"
else
    echo "ℹ️  Image does not exist"
fi

echo ""
echo "==================================="
echo "Cleanup complete!"
echo "==================================="
