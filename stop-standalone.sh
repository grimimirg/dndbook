#!/bin/bash

echo "==================================="
echo "Stopping D&D Book (Standalone Mode)"
echo "==================================="
echo ""

# Check if tmux sessions exist
if command -v tmux &> /dev/null; then
    if tmux has-session -t dndbook-backend 2>/dev/null; then
        echo "Stopping backend tmux session..."
        tmux kill-session -t dndbook-backend
        echo "✓ Backend stopped"
    fi
    
    if tmux has-session -t dndbook-frontend 2>/dev/null; then
        echo "Stopping frontend tmux session..."
        tmux kill-session -t dndbook-frontend
        echo "✓ Frontend stopped"
    fi
fi

# Kill processes by name
echo ""
echo "Stopping any remaining processes..."

# Stop Python processes (backend)
pkill -f "python.*main.py" 2>/dev/null && echo "✓ Backend processes stopped" || echo "  No backend processes found"

# Stop Vite dev server (frontend)
pkill -f "vite" 2>/dev/null && echo "✓ Frontend processes stopped" || echo "  No frontend processes found"

# Stop PostgreSQL container
echo ""
echo "Stopping PostgreSQL container..."
docker stop dndbook-postgres 2>/dev/null && echo "✓ PostgreSQL stopped" || echo "  PostgreSQL container not running"

echo ""
echo "==================================="
echo "D&D Book stopped"
echo "==================================="
echo ""
echo "Note: PostgreSQL container is stopped but not removed."
echo "To remove it: docker rm dndbook-postgres"
echo "To remove data: docker volume rm dndbook-postgres-data"
echo ""
