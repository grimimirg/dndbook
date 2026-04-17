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

4. Update `.env` with your configuration

5. Create virtual environment:

```bash
uv venv
source .venv/bin/activate  # On Linux/macOS
# or
.venv\Scripts\activate  # On Windows
```

6. Install dependencies:

```bash
uv pip install .
```

7. Initialize database (if not using mock mode):

```bash
./init-db.sh
```

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
- Backend `.env` file configured (see Backend Setup step 3-4)

### Setup

1. Create the `.env` file first:

```bash
cd be
cp .env.example .env
cd ..
```

The default values in `.env.example` are already configured for the Docker PostgreSQL setup.

2. Run the setup script:

```bash
./setup-postgres.sh
```

This script will:
- Download PostgreSQL 16 Alpine image
- Create and start a Docker container
- Initialize the database tables
- Test the connection

3. Start the backend:

```bash
cd be
source .venv/bin/activate
python app.py
```

### Cleanup

To remove the PostgreSQL container and data:

```bash
./cleanup-postgres.sh
```

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
