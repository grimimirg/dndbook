# D&D Book

A web application for managing D&D campaigns with a Facebook-style post feed interface.

## Quick Setup (Recommended)

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

## Quick Start with Docker

### Prerequisites

- Docker & Docker Compose
- PostgreSQL database (accessible from your network)

### Setup

1. Clone the repository

2. Create `.env` files for backend and frontend:

```bash
cd be
cp .env.example .env
# Edit be/.env with your PostgreSQL credentials

cd ../fe
cp .env.example .env
# Edit fe/.env if needed (default values should work)
```

3. Build and run with Docker Compose:

```bash
cd ..
docker-compose up --build
```

The application will be available at:

- Frontend: `http://localhost`
- Backend API: `http://localhost:5000`

### Initial Database Setup

After starting the backend container, initialize the database:

```bash
docker exec -it dndbook-backend ./init-db.sh
```

This creates the database tables and a default admin user:
- **Username**: `admin`
- **Email**: `admin@dndbook.local`
- **Password**: Value from `ADMIN_PASSWORD` in `be/.env` (defaults to `admin123` if not set)

**Important**: Make sure to set a secure `ADMIN_PASSWORD` in your `be/.env` file before running the initialization script.

## Local Development

### Backend Setup

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

### Frontend Setup

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

## PostgreSQL Setup with Docker

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

**Important**: Verify that `DATABASE_URL` in `.env` matches the Docker container configuration:
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

## Mock Data Mode

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

- 3 pre-configured campaigns
- 10 sample posts with realistic data
- No database connection required

## Internationalization (i18n)

The application supports multiple languages. Current supported languages are:

- English
- Italian
- German
- French
- Spanish
