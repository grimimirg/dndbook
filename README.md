# 🎲 D&D Book

> 📖 A web application for managing D&D campaigns with a Facebook-style post feed interface.

## 📑 Table of Contents

- [🔧 Setup Scripts Overview](#-setup-scripts-overview)
  - [Deployment Scenarios](#deployment-scenarios)
- [⚡ Quick Setup (Recommended)](#-quick-setup-recommended)
- [🐳 Quick Start with Docker Compose (Recommended for Production)](#-quick-start-with-docker-compose-recommended-for-production)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
  - [Initial Database Setup](#initial-database-setup)
  - [Data Persistence](#data-persistence)
  - [Stopping the Application](#stopping-the-application)
  - [Viewing Logs](#viewing-logs)
- [💻 Local Development](#-local-development)
  - [🔧 Backend Setup](#-backend-setup)
  - [🎨 Frontend Setup](#-frontend-setup)
- [🗄️ PostgreSQL Setup with Docker](#️-postgresql-setup-with-docker)
  - [Prerequisites](#prerequisites-1)
  - [Setup](#setup-1)
  - [Cleanup](#cleanup)
- [🎭 Mock Data Mode](#-mock-data-mode)
  - [Mock Credentials](#mock-credentials)
- [🌍 Internationalization (i18n)](#-internationalization-i18n)
- [🏠 Homelab Integration (IaC)](#-homelab-integration-iac)
  - [Template Files](#template-files)
  - [Required Environment Variables](#required-environment-variables)
  - [Architecture](#architecture)
  - [Services](#services)
  - [Domain Configuration](#domain-configuration)
  - [Nginx Configuration](#nginx-configuration)
  - [Setup Instructions](#setup-instructions)
  - [Notes](#notes)

## 🔧 Setup Scripts Overview

This project includes several setup scripts for different deployment scenarios:

| Script | Location | Purpose | When to Use |
|--------|----------|---------|-------------|
| `setup.sh` | Root | Complete local development setup | First time local development |
| `setup.sh` | `be/` | Backend-only local setup | Backend development only |
| `setup.sh` | `fe/` | Frontend-only local setup | Frontend development only |
| `setup-postgres.sh` | `be/` | Creates local PostgreSQL container | Local development without Docker Compose |
| `init-db.sh` | `be/` | Initializes database tables and admin user | Manual database initialization (auto in Docker) |
| `docker-entrypoint.sh` | `be/` | Docker container entrypoint | **Automatic** - runs in Docker containers |

### Deployment Scenarios

**🐳 Docker Compose (Production/Testing)**
- Uses: `docker-compose.yml`
- Database: Included PostgreSQL container
- Initialization: **Automatic** via `docker-entrypoint.sh`
- No manual scripts needed

**🏠 Homelab (IaC)**
- Uses: `docker-compose.yaml.template` + `nginx.conf.template`
- Database: External `shared_postgres`
- Initialization: **Automatic** via `docker-entrypoint.sh`
- No manual scripts needed

**💻 Local Development**
- Uses: `setup.sh` scripts
- Database: Local PostgreSQL via `setup-postgres.sh` OR existing instance
- Initialization: Via `init-db.sh` (called by setup scripts)
- Manual setup required

## ⚡ Quick Setup (Recommended)

The fastest way to get started is using the automated setup script:

```bash
./setup.sh
```

This script will:
- Check and install prerequisites (uv)
- Set up both backend and frontend
- Create environment files
- Install all dependencies
- Guide you through database initialization

**Individual setup scripts are also available:**
- Backend only: `cd be && ./setup.sh`
- Frontend only: `cd fe && ./setup.sh`

## 🐳 Quick Start with Docker Compose (Recommended for Production)

### Prerequisites

- 🐳 Docker & Docker Compose installed and running

> ℹ️ **Note**: PostgreSQL is **included** in the Docker Compose setup. You don't need to install or configure a separate database.

### Setup

1. Clone the repository

2. Create and configure `.env` files:

**🔧 Backend** (`be/.env`):
```bash
cd be
cp .env.example .env
```

Edit `be/.env` and set at minimum:
```bash
# Security - CHANGE THESE IN PRODUCTION!
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
ADMIN_PASSWORD=your-secure-admin-password

# Database - DO NOT CHANGE (managed by docker-compose)
DATABASE_URL=postgresql://dndbook_user:dndbook_password@postgres:5432/dndbook_db

# Mock Data - set to false for production
MOCK_DATA=false
```

**🎨 Frontend** (`fe/.env`):
```bash
cd ../fe
cp .env.example .env
```

Edit `fe/.env` and set:
```bash
# Backend API URL
VITE_API_URL=http://localhost:5000

# Mock Data - set to false for production
VITE_MOCK_DATA=false

# Optional: Locales (defaults to en,it,de,fr,es if not set)
VITE_AVAILABLE_LOCALES=en,it,de,fr,es

# Optional: Pagination (defaults shown)
VITE_POSTS_PER_PAGE=10
VITE_POST_PREVIEW_LIMIT=200
```

3. Build and start all services:

```bash
cd ..
docker compose up --build
```

> 💡 **Note**: Use `docker compose` (without hyphen) for modern Docker installations. If you have an older version, use `docker-compose`.

The application will be available at:
- 🌐 **Frontend**: `http://localhost`
- 🔌 **Backend API**: `http://localhost:5000`
- 🗄️ **PostgreSQL**: `localhost:5432` (internal to Docker network)

### Initial Database Setup

The database is **automatically initialized** on first startup! The backend container will:
1. Wait for PostgreSQL to be ready
2. Check if tables exist
3. If not, create tables and default admin user
4. Start the Flask application

Default admin credentials:
- **Username**: `admin`
- **Email**: `admin@dndbook.local`
- **Password**: Value from `ADMIN_PASSWORD` in `be/.env`

> ⚠️ **Important**: Make sure to set a secure `ADMIN_PASSWORD` in your `be/.env` file before starting the containers.

> 💡 **Manual initialization**: If needed, you can manually run `docker exec -it dndbook-backend ./init-db.sh`

### Data Persistence

PostgreSQL data is stored in a Docker volume named `dndbook-postgres-data`. This means:
- ✅ Your data persists even if you stop/restart containers
- ⚠️ To completely remove all data, you need to delete the volume: `docker volume rm dndbook-postgres-data`

### Stopping the Application

```bash
# Stop containers (data is preserved) ✅
docker compose down

# Stop and remove volumes ⚠️ WARNING: deletes all data
docker compose down -v
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
```

## 💻 Local Development

### 🔧 Backend Setup

1. Install uv:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Navigate to backend directory:

```bash
cd be
```

3. Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

4. Update `.env` with your configuration:
   - Set `DATABASE_URL` to your PostgreSQL connection string
   - Set `ADMIN_PASSWORD` to configure the default admin user password (default: `admin123`)

5. Create virtual environment with Python 3.11+:

```bash
# Recommended: use Python 3.14
uv venv --python 3.14

# Activate
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows

# Verify Python version
python --version  # Should show 3.11 or higher
```

6. Install dependencies:

```bash
uv pip install .
```

7. Initialize database (if not using mock mode):

```bash
./init-db.sh
```

This will create the database tables and a default admin user:
- **Username**: `admin`
- **Email**: `admin@dndbook.local`
- **Password**: Value from `ADMIN_PASSWORD` in `.env` (defaults to `admin123` if not set)

8. Run development server:

```bash
python app.py
```

Backend will be available at `http://localhost:5000`

### 🎨 Frontend Setup

1. Navigate to frontend directory:

```bash
cd fe
```

2. Create `.env` file from `.env.example`:

```bash
cp .env.example .env
```

3. Install dependencies:

```bash
npm install
```

4. Run development server:

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

## 🗄️ PostgreSQL Setup with Docker

For local development with a real database, you can use the provided setup script:

### Prerequisites

- Docker installed and running
- `uv` installed (see Backend Setup step 1)
- Python 3.11+ available

### Setup

1. Create and configure the `.env` file:

```bash
cd be
cp .env.example .env
```

> ⚠️ **Important**: Verify that `DATABASE_URL` in `.env` matches the Docker container configuration:
```
DATABASE_URL=postgresql://dndbook_user:dndbook_password@localhost:5432/dndbook_db
```

Also set a secure password for the default admin user:
```
ADMIN_PASSWORD=your_secure_password_here
```

2. Create virtual environment with the correct Python version:

```bash
# Remove old venv if exists
rm -rf .venv

# Create venv with Python 3.11+ (recommended: 3.14)
uv venv --python 3.14

# Activate
source .venv/bin/activate

# Install dependencies
uv pip install .
```

3. Run the setup script (with venv activated):

```bash
# Make sure you're in the be/ directory
./setup-postgres.sh
```

This script will:
- Check that Docker is installed
- Download PostgreSQL 16 Alpine image
- Create and start a Docker container
- Verify `.env` file exists
- Initialize the database tables
- Create a default admin user (username: `admin`, password from `ADMIN_PASSWORD` in `.env`)
- Test the connection

4. Start the backend:

```bash
# From be/ directory
python app.py
```

Backend will be available at `http://localhost:5000`

### Cleanup

To remove the PostgreSQL container and data:

```bash
# From project root
./cleanup-postgres.sh
```

Note: `cleanup-postgres.sh` is in the project root, while `setup-postgres.sh` is in `be/` directory.

## 🎭 Mock Data Mode

For development without a database, you can enable mock data mode:

### Backend

Edit `be/.env`:

```
MOCK_DATA=true
```

### Frontend

Edit `fe/.env`:

```
VITE_MOCK_DATA=true
```

### Mock Credentials

- **Username**: `admin`
- **Password**: any (in mock mode)

Mock mode includes:

- 🎯 3 pre-configured campaigns
- 📝 10 sample posts with realistic data
- 🚫 No database connection required

## 🌍 Internationalization (i18n)

The application supports multiple languages. Current supported languages are:

- 🇬🇧 English
- 🇮🇹 Italian
- 🇩🇪 German
- 🇫🇷 French
- 🇪🇸 Spanish

## 🏠 Homelab Integration (IaC)

This application can be integrated into an Infrastructure-as-Code (IaC) homelab setup using template files.

### Template Files

The project includes two template files for homelab deployment:

- **`docker-compose.yaml.template`**: Docker Compose configuration with environment variable placeholders
- **`nginx.conf.template`**: Nginx reverse proxy configuration with environment variable placeholders

### Required Environment Variables

These variables should be defined in your homelab's `.env` file:

| Variable | Description |
|----------|-------------|
| `SHARED_NETWORK` | Docker network shared across homelab services |
| `HOST_UID` | User ID for container permissions |
| `HOST_GID` | Group ID for container permissions |
| `POSTGRES_USER` | PostgreSQL username (from existing homelab instance) |
| `POSTGRES_PASSWORD` | PostgreSQL password (from existing homelab instance) |
| `DOMAIN` | Your homelab domain | `example.com` |
| `DOLLAR` | Dollar sign for nginx variable escaping |

### Architecture

The homelab setup assumes:

- **External PostgreSQL**: Uses an existing `shared_postgres` container in your homelab
- **Shared Network**: All services communicate through `${SHARED_NETWORK}`
- **Nginx Reverse Proxy**: External nginx handles SSL termination and routing
- **No Authelia**: Direct access without authentication layer

### Services

**Backend** (`dndbook_backend`):
- Connects to `shared_postgres:5432`
- Creates/uses database `dndbook_db`
- Exposes port 5000 internally

**Frontend** (`dndbook_frontend`):
- Serves Vue.js application
- Exposes port 80 internally

### Domain Configuration

The application will be accessible at:
- `dnd.${DOMAIN}` (production with HTTPS)
- `dnd.localhost` (local development)
- `dnd.jarvis` (local network)

### Nginx Configuration

The nginx template provides:

- **HTTP (port 80)**: Automatic redirect to HTTPS for production domain
- **HTTPS (port 443)**: SSL-enabled access with Let's Encrypt certificates
  - Frontend proxy: `http://dndbook_frontend:80`
  - Backend API proxy: `http://dndbook_backend:5000/apiService`

### Setup Instructions

1. **Copy template files** to your homelab structure:
   ```bash
   # Copy to your homelab services directory
   cp docker-compose.yaml.template /path/to/homelab/services/dndbook/
   
   # Copy to your homelab nginx configuration directory
   cp nginx.conf.template /path/to/homelab/nginx/conf.d/dndbook.conf.template
   ```

2. **Create the database** (first time only):
   ```bash
   docker exec -it shared_postgres psql -U ${POSTGRES_USER} -c "CREATE DATABASE dndbook_db;"
   ```

3. **Create data directory**:
   ```bash
   mkdir -p /path/to/homelab/data/dndbook/uploads
   chown ${HOST_UID}:${HOST_GID} /path/to/homelab/data/dndbook/uploads
   ```

4. **Process templates** using your homelab's template substitution mechanism to generate final `docker-compose.yaml` and `nginx.conf` files

5. **Start services**:
   ```bash
   docker compose up -d dndbook_backend dndbook_frontend
   ```
   
   > ℹ️ **Note**: The backend will automatically initialize the database on first startup if tables don't exist.

6. **Reload nginx**:
   ```bash
   docker exec nginx nginx -t
   docker exec nginx nginx -s reload
   ```

### Notes

- The PostgreSQL service in `docker-compose.yml` is **not used** in homelab deployments
- SSL certificates are expected at `/etc/letsencrypt/live/${DOMAIN}/`
- Upload files are stored in `../data/dndbook/uploads` relative to the docker-compose location
- The application runs without authentication (no Authelia integration)
