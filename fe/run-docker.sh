#!/bin/bash

set -e

IMAGE_NAME="dndbook-frontend"
CONTAINER_NAME="dndbook-frontend"
PORT=80

echo "==================================="
echo "D&D Book Frontend - Docker Setup"
echo "==================================="

if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file before running the application."
    echo "You can copy .env.example: cp .env.example .env"
    exit 1
fi

echo "Checking Docker..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi
echo "✓ Docker found"

echo ""
echo "Stopping existing container (if any)..."
docker stop $CONTAINER_NAME 2>/dev/null || true
docker rm $CONTAINER_NAME 2>/dev/null || true
echo "✓ Cleanup complete"

echo ""
echo "Building Docker image (without cache)..."
docker build --no-cache -t $IMAGE_NAME .
echo "✓ Image built successfully"

echo ""
echo "Starting container..."
docker run -d \
    --name $CONTAINER_NAME \
    -p $PORT:80 \
    $IMAGE_NAME

echo "✓ Container started"

echo ""
echo "==================================="
echo "Application running!"
echo "==================================="
echo "Container name: $CONTAINER_NAME"
echo "Port: $PORT"
echo "URL: http://localhost:$PORT"
echo "Logs: docker logs -f $CONTAINER_NAME"
echo "Stop: docker stop $CONTAINER_NAME"
echo "==================================="
