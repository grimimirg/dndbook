#!/bin/bash

set -e

echo "==================================="
echo "D&D Book - Docker Compose Mode"
echo "==================================="
echo ""

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null && ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

# Determine docker compose command
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif docker-compose version &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "❌ Docker Compose not found. Please install Docker Compose."
    exit 1
fi

echo "Using: $DOCKER_COMPOSE"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "   Docker Compose requires a .env file with all configuration variables."
    echo ""
    echo "   Create it from the example:"
    echo "   cp .env.example .env"
    echo ""
    echo "   Then edit .env with your configuration values."
    exit 1
fi
echo "✓ .env file found"
echo ""

# Validate required environment variables
echo "Validating environment variables..."
REQUIRED_VARS=("POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB" "SECRET_KEY" "JWT_SECRET_KEY" "ADMIN_PASSWORD" "MOCK_DATA" "UPLOAD_FOLDER" "MAX_CONTENT_LENGTH" "POSTS_PER_PAGE" "VITE_API_URL" "VITE_MOCK_DATA" "VITE_AVAILABLE_LOCALES" "VITE_POSTS_PER_PAGE" "VITE_POST_PREVIEW_LIMIT")
MISSING_VARS=()

# Load .env file
export $(grep -v '^#' .env | xargs)

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -ne 0 ]; then
    echo "❌ Missing required environment variables in .env:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "Please update your .env file with all required variables."
    echo "See .env.example for reference."
    exit 1
fi
echo "✓ All required variables present"
echo ""

# Stop any existing containers
echo "Stopping existing containers (if any)..."
$DOCKER_COMPOSE -f docker-compose.standalone.yaml down 2>/dev/null || true

# Remove any orphaned containers with the same names
echo "Removing any orphaned containers..."
docker rm -f dndbook-postgres dndbook-backend dndbook-frontend 2>/dev/null || true
echo "✓ Cleanup complete"
echo ""

# Build and start containers
echo "Building and starting containers..."
echo "This may take a few minutes on first run..."
echo ""

$DOCKER_COMPOSE -f docker-compose.standalone.yaml up -d --build

if [ $? -eq 0 ]; then
    echo ""
    echo "==================================="
    echo "D&D Book is starting!"
    echo "==================================="
    echo ""
    echo "Waiting for services to be ready..."
    sleep 5
    
    # Check container status
    echo ""
    echo "Container status:"
    $DOCKER_COMPOSE -f docker-compose.standalone.yaml ps
    
    echo ""
    echo "==================================="
    echo "Services:"
    echo "  🗄️  PostgreSQL: localhost:5432"
    echo "  🔌 Backend:     http://localhost:5000"
    echo "  🌐 Frontend:    http://localhost"
    echo ""
    echo "Credentials:"
    echo "  Username: admin"
    echo "  Password: (check .env ADMIN_PASSWORD, default: admin123)"
    echo ""
    echo "Useful commands:"
    echo "  View logs:        $DOCKER_COMPOSE -f docker-compose.standalone.yaml logs -f"
    echo "  Stop:             $DOCKER_COMPOSE -f docker-compose.standalone.yaml down"
    echo "  Stop + delete DB: $DOCKER_COMPOSE -f docker-compose.standalone.yaml down -v"
    echo "  Restart:          $DOCKER_COMPOSE -f docker-compose.standalone.yaml restart"
    echo ""
    echo "Or use: ./stop-docker.sh"
    echo "==================================="
else
    echo ""
    echo "❌ Failed to start containers"
    echo "Check logs with: $DOCKER_COMPOSE -f docker-compose.standalone.yaml logs"
    exit 1
fi
