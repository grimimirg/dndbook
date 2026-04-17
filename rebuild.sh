#!/bin/bash

echo "Cleaning up Docker containers and images..."

echo "Stopping containers..."
docker-compose down

echo "Removing containers..."
docker rm -f dndbook-backend dndbook-frontend 2>/dev/null || true

echo "Removing images..."
docker rmi dndbook-backend dndbook-frontend 2>/dev/null || true

echo "Cleaning up dangling images and build cache..."
docker image prune -f

echo "Removing volumes..."
docker volume prune -f

echo ""
echo "Building and starting fresh containers..."
docker-compose up --build -d

echo ""
echo "Done! Containers are being rebuilt."
echo ""
echo "Container status:"
docker-compose ps
