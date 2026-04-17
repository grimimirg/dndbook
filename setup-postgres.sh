#!/bin/bash

set -e

echo "Setup PostgreSQL for D&D Book"
echo "============================="

CONTAINER_NAME="dndbook-postgres"
POSTGRES_USER="dndbook_user"
POSTGRES_PASSWORD="dndbook_password"
POSTGRES_DB="dndbook_db"
POSTGRES_PORT="5432"

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

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install it before continuing."
    exit 1
fi
print_success "Docker found"

if [ "$(docker ps -aq -f name=$CONTAINER_NAME)" ]; then
    print_warning "Container $CONTAINER_NAME already exists"
    read -p "Do you want to remove and recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Removing existing container..."
        docker stop $CONTAINER_NAME 2>/dev/null || true
        docker rm $CONTAINER_NAME 2>/dev/null || true
        print_success "Container removed"
    else
        print_warning "Using existing container"
        docker start $CONTAINER_NAME 2>/dev/null || true
        print_success "Container started"
        exit 0
    fi
fi

echo ""
echo "Downloading PostgreSQL image..."
docker pull postgres:16-alpine
print_success "Image downloaded"

echo ""
echo "Creating PostgreSQL container..."
docker run -d \
    --name $CONTAINER_NAME \
    -e POSTGRES_USER=$POSTGRES_USER \
    -e POSTGRES_PASSWORD=$POSTGRES_PASSWORD \
    -e POSTGRES_DB=$POSTGRES_DB \
    -p $POSTGRES_PORT:5432 \
    -v dndbook-postgres-data:/var/lib/postgresql/data \
    postgres:16-alpine

print_success "Container created and started"

echo ""
echo "Waiting for PostgreSQL to be ready..."
sleep 5

if [ "$(docker ps -q -f name=$CONTAINER_NAME)" ]; then
    print_success "PostgreSQL is running"
else
    print_error "Error: container is not running"
    exit 1
fi

echo ""
echo "Testing database connection..."
if docker exec $CONTAINER_NAME pg_isready -U $POSTGRES_USER > /dev/null 2>&1; then
    print_success "Database connection successful"
else
    print_error "Unable to connect to database"
    exit 1
fi

echo ""
echo "Checking .env file..."
ENV_FILE="be/.env"

if [ ! -f "$ENV_FILE" ]; then
    print_error ".env file not found in be/ directory"
    echo ""
    echo "Please create be/.env file with the following configuration:"
    echo ""
    echo "DATABASE_URL=postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:$POSTGRES_PORT/$POSTGRES_DB"
    echo "SECRET_KEY=your-secret-key"
    echo "JWT_SECRET_KEY=your-jwt-secret-key"
    echo "MOCK_DATA=false"
    echo "UPLOAD_FOLDER=uploads"
    echo "MAX_CONTENT_LENGTH=16777216"
    echo "POSTS_PER_PAGE=10"
    echo ""
    echo "You can copy from be/.env.example if available"
    exit 1
fi

print_success ".env file found"

echo ""
echo "Initializing database..."
cd be

if [ ! -d ".venv" ]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv .venv
    print_success "Virtual environment created"
fi

source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -e .

echo "Creating tables..."
./init-db.sh

print_success "Database initialized successfully"

cd ..

echo ""
echo "============================="
echo "Setup completed successfully!"
echo "============================="
echo ""
echo "Connection information:"
echo "  Host: localhost"
echo "  Port: $POSTGRES_PORT"
echo "  Database: $POSTGRES_DB"
echo "  User: $POSTGRES_USER"
echo "  Password: $POSTGRES_PASSWORD"
echo ""
echo "Connection String:"
echo "  postgresql://$POSTGRES_USER:$POSTGRES_PASSWORD@localhost:$POSTGRES_PORT/$POSTGRES_DB"
echo ""
echo "Useful Docker commands:"
echo "  Start:   docker start $CONTAINER_NAME"
echo "  Stop:    docker stop $CONTAINER_NAME"
echo "  Remove:  docker rm $CONTAINER_NAME"
echo "  Logs:    docker logs $CONTAINER_NAME"
echo "  Shell:   docker exec -it $CONTAINER_NAME psql -U $POSTGRES_USER -d $POSTGRES_DB"
echo ""
echo "To start the application:"
echo "  Backend:  cd be && source .venv/bin/activate && python app.py"
echo "  Frontend: cd fe && npm install && npm run dev"
echo ""
