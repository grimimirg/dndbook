#!/bin/bash

set -e

CONTAINER_NAME="dndbook-postgres"
VOLUME_NAME="dndbook-postgres-data"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

echo "Cleanup PostgreSQL for D&D Book"
echo "================================"
echo ""

read -p "Do you want to remove the PostgreSQL container and data? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_warning "Operation cancelled"
    exit 0
fi

if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    echo "Stopping container..."
    docker stop $CONTAINER_NAME
    print_success "Container stopped"
fi

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    echo "Removing container..."
    docker rm $CONTAINER_NAME
    print_success "Container removed"
fi

echo ""
read -p "Do you also want to remove the volume with database data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ "$(docker volume ls -q -f name=$VOLUME_NAME)" ]; then
        echo "Removing volume..."
        docker volume rm $VOLUME_NAME
        print_success "Volume removed"
    else
        print_warning "Volume not found"
    fi
else
    print_warning "Volume kept (data will be preserved)"
fi

echo ""
print_success "Cleanup completed!"
