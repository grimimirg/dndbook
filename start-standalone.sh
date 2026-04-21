#!/bin/bash

set -e

echo "==================================="
echo "D&D Book - Standalone Mode"
echo "==================================="
echo ""
echo "This will start:"
echo "  - PostgreSQL in Docker container"
echo "  - Backend in Python virtual environment"
echo "  - Frontend in Node.js dev server"
echo ""

# Check if tmux is available
if ! command -v tmux &> /dev/null; then
    echo "⚠️  tmux not found. Install it for better experience:"
    echo "   sudo apt-get install tmux  # Debian/Ubuntu"
    echo "   sudo dnf install tmux      # Fedora/RHEL"
    echo ""
    echo "Continuing without tmux..."
    USE_TMUX=false
else
    USE_TMUX=true
fi

# Backend
echo "==================================="
echo "Starting Backend..."
echo "==================================="

cd be

if [ ! -f ".env" ]; then
    echo "❌ Backend .env file not found!"
    echo "Please create be/.env file before running."
    echo "You can copy: cp be/.env.example be/.env"
    exit 1
fi

if $USE_TMUX; then
    # Start backend in tmux session
    tmux new-session -d -s dndbook-backend "cd $(pwd) && ./run-standalone.sh"
    echo "✓ Backend started in tmux session 'dndbook-backend'"
    echo "  Attach with: tmux attach -t dndbook-backend"
else
    # Start backend in background
    nohup ./run-standalone.sh > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo "✓ Backend started (PID: $BACKEND_PID)"
    echo "  Logs: tail -f backend.log"
fi

cd ..

# Wait for backend to be ready
echo ""
echo "Waiting for backend to be ready..."
sleep 5

# Frontend
echo ""
echo "==================================="
echo "Starting Frontend..."
echo "==================================="

cd fe

if [ ! -f ".env" ]; then
    echo "❌ Frontend .env file not found!"
    echo "Please create fe/.env file before running."
    echo "You can copy: cp fe/.env.example fe/.env"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

if $USE_TMUX; then
    # Start frontend in tmux session
    tmux new-session -d -s dndbook-frontend "cd $(pwd) && npm run dev"
    echo "✓ Frontend started in tmux session 'dndbook-frontend'"
    echo "  Attach with: tmux attach -t dndbook-frontend"
else
    # Start frontend in background
    nohup npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "✓ Frontend started (PID: $FRONTEND_PID)"
    echo "  Logs: tail -f frontend.log"
fi

cd ..

echo ""
echo "==================================="
echo "D&D Book is starting!"
echo "==================================="
echo ""
echo "Services:"
echo "  🗄️  PostgreSQL: localhost:5432"
echo "  🔌 Backend:     http://localhost:5000"
echo "  🌐 Frontend:    http://localhost:5173"
echo ""

if $USE_TMUX; then
    echo "Tmux sessions:"
    echo "  - dndbook-backend  (tmux attach -t dndbook-backend)"
    echo "  - dndbook-frontend (tmux attach -t dndbook-frontend)"
    echo ""
    echo "List all sessions: tmux ls"
    echo "Kill all sessions: tmux kill-session -t dndbook-backend && tmux kill-session -t dndbook-frontend"
else
    echo "Background processes:"
    echo "  - Backend PID:  $BACKEND_PID"
    echo "  - Frontend PID: $FRONTEND_PID"
    echo ""
    echo "Stop all: ./stop-standalone.sh"
fi

echo ""
echo "Credentials:"
echo "  Username: admin"
echo "  Password: (check be/.env ADMIN_PASSWORD)"
echo ""
echo "==================================="
