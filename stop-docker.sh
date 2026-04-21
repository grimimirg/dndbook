#!/bin/bash

echo "==================================="
echo "Stopping D&D Book (Docker Mode)"
echo "==================================="
echo ""

# Determine docker compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ Docker Compose not found"
    exit 1
fi

echo "Using: $DOCKER_COMPOSE"
echo ""

# Ask if user wants to preserve data
echo "How do you want to stop?"
echo "  1) Stop containers (preserve data) - RECOMMENDED"
echo "  2) Stop and remove volumes (delete all data)"
echo ""
read -p "Choose [1/2] (default: 1): " choice
choice=${choice:-1}

if [ "$choice" = "2" ]; then
    echo ""
    echo "⚠️  WARNING: This will DELETE all database data!"
    read -p "Are you sure? [y/N]: " confirm
    if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
        echo ""
        echo "Stopping and removing containers and volumes..."
        $DOCKER_COMPOSE -f docker-compose.standalone.yaml down -v
        echo "✓ Containers and volumes removed"
    else
        echo "Cancelled"
        exit 0
    fi
else
    echo ""
    echo "Stopping containers..."
    $DOCKER_COMPOSE -f docker-compose.standalone.yaml down
    echo "✓ Containers stopped (data preserved)"
fi

echo ""
echo "==================================="
echo "D&D Book stopped"
echo "==================================="
echo ""

if [ "$choice" != "2" ]; then
    echo "Data is preserved in Docker volumes."
    echo "To start again: ./start-docker.sh"
    echo ""
    echo "To delete all data:"
    echo "  docker volume rm dndbook-postgres-data"
fi

echo ""
