#!/bin/bash

# Sync Frontend Environment Variables from Root
# This script creates .env.local from root .env VITE_* variables

set -e

echo "Syncing frontend environment variables from root .env..."

# Check if root .env exists
if [ ! -f "../.env" ]; then
    echo "⚠️  Root .env not found, skipping sync"
    exit 0
fi

# Extract VITE_* variables from root .env
grep '^VITE_' ../.env > .env.local 2>/dev/null || true

if [ -s .env.local ]; then
    echo "✓ Frontend .env.local created with variables from root .env:"
    cat .env.local | sed 's/=.*//' | sed 's/^/  - /'
else
    echo "ℹ️  No VITE_* variables found in root .env"
    rm -f .env.local
fi
