# D&D Campaign Manager

A web application for managing D&D campaigns with a Facebook-style post feed interface.

## Features

- **Authentication**: JWT-based login system
- **Campaign Management**: Create and organize multiple campaigns
- **Post Feed**: Facebook-style feed with infinite scroll
- **Image Support**: Multiple images per post with slideshow
- **Tree Navigation**: Expandable sidebar for campaign/post navigation
- **Sorting**: Sort posts by creation date or last update
- **Internationalization**: Support for English, Italian, and German
- **Mock Data Mode**: Development mode with mock data (no database required)
- **Responsive Design**: Clean, simple UI

## Tech Stack

### Backend
- Python 3.11
- Flask (REST API)
- SQLAlchemy (ORM)
- SQL Server (Database)
- JWT Authentication
- uv (Package manager)

### Frontend
- Vue 3 (Composition API)
- Pinia (State management)
- Vue Router
- Vue I18n (Internationalization)
- Axios (HTTP client)
- Vite (Build tool)

## Quick Start with Docker

### Prerequisites
- Docker & Docker Compose
- SQL Server database (accessible from your network)

### Setup

1. Clone the repository

2. Create `.env` files for backend and frontend:
```bash
cd be
cp .env.example .env
# Edit be/.env with your SQL Server credentials

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
docker exec -it dndbook-backend flask --app run init-db
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

5. Install dependencies:
```bash
uv pip install -r pyproject.toml
```

6. Initialize database (if not using mock mode):
```bash
flask --app run init-db
```

7. Run development server:
```bash
python run.py
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
- **Username**: `dungeon_master`
- **Password**: any (in mock mode)

Mock mode includes:
- 3 pre-configured campaigns
- 10 sample posts with realistic data
- No database connection required

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login (returns JWT token)

### Campaigns (Protected)
- `GET /api/campaigns` - List user's campaigns
- `POST /api/campaigns` - Create campaign
- `GET /api/campaigns/{id}` - Get campaign details
- `PUT /api/campaigns/{id}` - Update campaign
- `DELETE /api/campaigns/{id}` - Delete campaign

### Posts (Protected)
- `GET /api/campaigns/{id}/posts` - List posts (with pagination)
- `POST /api/posts` - Create post
- `GET /api/posts/{id}` - Get post details
- `PUT /api/posts/{id}` - Update post
- `DELETE /api/posts/{id}` - Delete post
- `POST /api/posts/{id}/images` - Upload image

All protected endpoints require:
```
Authorization: Bearer <JWT_TOKEN>
```

## Project Structure

### Backend (`/be`)
```
be/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── models.py            # SQLAlchemy models
│   ├── auth.py              # JWT authentication utilities
│   ├── mock_data.py         # Mock data for development
│   └── routes/
│       ├── auth.py          # Authentication endpoints
│       ├── campaigns.py     # Campaign CRUD endpoints
│       └── posts.py         # Post CRUD endpoints
├── run.py                   # Application entry point
├── pyproject.toml           # Python dependencies
├── Dockerfile
└── .env.example
```

### Frontend (`/fe`)
```
fe/
├── src/
│   ├── components/          # Reusable Vue components
│   │   ├── Sidebar.vue
│   │   ├── PostCard.vue
│   │   └── PostCreator.vue
│   ├── views/               # Page components
│   │   ├── Login.vue
│   │   └── Home.vue
│   ├── stores/              # Pinia stores
│   │   ├── auth.js
│   │   ├── campaigns.js
│   │   └── posts.js
│   ├── services/            # API layer
│   │   ├── api.js
│   │   └── mockData.js
│   ├── locales/             # i18n translations
│   │   ├── en.yaml
│   │   ├── it.yaml
│   │   └── de.yaml
│   ├── router/              # Vue Router
│   ├── i18n.js              # i18n configuration
│   ├── main.js
│   └── App.vue
├── package.json
├── vite.config.js
├── Dockerfile
└── .env.example
```

## Internationalization

The application supports three languages:
- **English** (en)
- **Italian** (it)
- **German** (de)

Language can be changed via the dropdown selector in the header. The selected language is persisted in localStorage.

Translation files are located in `/fe/src/locales/` as YAML files.

## Database Schema

### Users
- id, username, email, password_hash, created_at

### Campaigns
- id, name, description, owner_id, created_at, updated_at

### Posts
- id, campaign_id, author_id, title, content, created_at, updated_at

### Images
- id, post_id, file_path, order_index, created_at

## Environment Variables

### Backend (`be/.env`)
```
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
MOCK_DATA=false
DATABASE_URL=mssql+pyodbc://user:pass@host:1433/dbname?driver=ODBC+Driver+17+for+SQL+Server
UPLOAD_FOLDER=uploads
MAX_CONTENT_LENGTH=16777216
```

### Frontend (`fe/.env`)
```
VITE_API_URL=http://localhost:5000
VITE_MOCK_DATA=false
```

## License

MIT
