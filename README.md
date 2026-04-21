# 📖 D&D Book

A web platform to manage your Dungeons & Dragons campaigns.

## 🚀 Quick Start

There are **two ways** to run the application. Choose the one that fits your needs:

### 🐳 Option 1: Docker (Recommended - Easiest)

**Best for:** You want to start everything with a single command, without installing anything on your computer.

**Requirements:**
- Docker installed on your computer

**Steps:**

1. **Configure the application**
   ```bash
   cp .env.example .env
   ```
   Then open the `.env` file and modify the values (especially passwords!).

2. **Start everything**
   ```bash
   ./start-docker.sh
   ```

3. **Open your browser**
   - Go to: http://localhost
   - Username: `admin`
   - Password: the one you set in `.env`

**To stop:**
```bash
./stop-docker.sh
```

---

### 💻 Option 2: Standalone (For Developers)

**Best for:** You want to develop or modify the code.

**Requirements:**
- Python 3.8+ installed
- Node.js 18+ installed
- Docker (only for PostgreSQL database)

**Steps:**

1. **Configure the application**
   ```bash
   cp .env.example .env
   ```
   Then open the `.env` file and modify the values.

2. **Start everything**
   ```bash
   ./start-standalone.sh
   ```
   This script will automatically start:
   - PostgreSQL database (in Docker)
   - Backend (Python/Flask)
   - Frontend (Vue.js)

3. **Open your browser**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000
   - Username: `admin`
   - Password: the one you set in `.env`

**To stop:**
```bash
./stop-standalone.sh
```

---

## 📁 Project Structure

```
dndbook/
├── .env                    # Main configuration (create this)
├── start-docker.sh         # Start with Docker
├── start-standalone.sh     # Start in development mode
├── be/                     # Backend (Python/Flask)
│   ├── .env               # Backend configuration (optional)
│   └── run-standalone.sh  # Start backend only
└── fe/                     # Frontend (Vue.js)
    ├── .env               # Frontend configuration (optional)
    └── run-standalone.sh  # Start frontend only
```

---

## ⚙️ Configuration

### Main `.env` File

The `.env` file in the root folder contains **all** the application configuration.

**Important variables to change:**

```bash
# PostgreSQL Database
POSTGRES_USER=dndbook_user
POSTGRES_PASSWORD=change-this-password      # ⚠️ IMPORTANT!
POSTGRES_DB=dndbook_db

# Security Keys (generate new keys for production!)
SECRET_KEY=change-this-key                  # ⚠️ IMPORTANT!
JWT_SECRET_KEY=change-this-key              # ⚠️ IMPORTANT!

# Admin Password
ADMIN_PASSWORD=admin123                      # ⚠️ IMPORTANT!
```

**To generate secure keys:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### Advanced Configuration (Optional)

If you want to customize only the backend or frontend:
- **Backend**: Create `be/.env` (variables here override those in root `.env`)
- **Frontend**: Create `fe/.env` (variables here override those in root `.env`)

---

## 🛠️ Useful Commands

### Docker
```bash
# View logs
docker compose -f docker-compose.standalone.yaml logs -f

# Restart services
docker compose -f docker-compose.standalone.yaml restart

# Stop and remove everything (including database!)
docker compose -f docker-compose.standalone.yaml down -v
```

### Standalone
```bash
# Start backend only
cd be && ./run-standalone.sh

# Start frontend only
cd fe && ./run-standalone.sh

# View active processes
ps aux | grep -E "python|vite"
```

---

## 🆘 Common Issues

### "Port already in use"
Another program is using the port. Stop the other program or change the port in `.env`.

### "Database connection failed"
Make sure Docker is running and the credentials in `.env` are correct.

### "Missing required environment variables"
You forgot to create the `.env` file. Run: `cp .env.example .env`

### Frontend can't connect to backend
Check that `VITE_API_URL` in `.env` is correct:
- Docker: leave empty or `VITE_API_URL=`
- Standalone: `VITE_API_URL=http://localhost:5000`

---

## 📝 Notes

- The `.env` file contains passwords and secret keys: **DO NOT share it** and **DO NOT upload it to Git**
- For production, always generate new random secret keys
- The database is saved in a Docker volume, so your data persists even after stopping the application
