#!/bin/bash

set -e

echo "==================================="
echo "Database Update Script"
echo "==================================="
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "[ERROR] .env file not found"
    echo "Please create .env file first:"
    echo "  cp .env.example .env"
    exit 1
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "[INFO] Virtual environment not activated"
    echo "Activating .venv..."
    if [ -f ".venv/bin/activate" ]; then
        source .venv/bin/activate
    else
        echo "[ERROR] Virtual environment not found"
        echo "Please create it first:"
        echo "  python3 -m venv .venv"
        exit 1
    fi
fi

echo "[INFO] Updating database schema..."
echo ""

# Execute Python code to update database
python << 'EOF'
import sys
import os
from sqlalchemy import inspect

# Import from the app package
from app import create_app, db
from app.models import User, Campaign, Character, Post, Comment, Image, CampaignInvite

# Create the Flask app
flask_app = create_app()

def get_table_columns(inspector, table_name):
    """Get column names and types for a table."""
    try:
        columns = inspector.get_columns(table_name)
        return {col['name']: str(col['type']) for col in columns}
    except Exception:
        return {}

def compare_table_structure(inspector, table_name, model_table):
    """Compare database table structure with model definition."""
    db_columns = get_table_columns(inspector, table_name)
    model_columns = {col.name: str(col.type) for col in model_table.columns}
    
    added_columns = set(model_columns.keys()) - set(db_columns.keys())
    removed_columns = set(db_columns.keys()) - set(model_columns.keys())
    
    changed_columns = []
    for col_name in set(model_columns.keys()) & set(db_columns.keys()):
        if model_columns[col_name] != db_columns[col_name]:
            changed_columns.append(col_name)
    
    return added_columns, removed_columns, changed_columns

try:
    with flask_app.app_context():
        # Get database inspector
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"[INFO] Existing tables in database: {', '.join(existing_tables) if existing_tables else 'none'}")
        print("")
        
        # Get all model tables
        model_tables = db.metadata.tables
        model_table_names = list(model_tables.keys())
        print(f"[INFO] Model tables defined: {', '.join(model_table_names)}")
        print("")
        
        # Find new tables
        new_tables = [table for table in model_table_names if table not in existing_tables]
        
        # Find tables that need updates
        tables_to_update = []
        for table_name in existing_tables:
            if table_name in model_tables:
                added, removed, changed = compare_table_structure(
                    inspector, table_name, model_tables[table_name]
                )
                if added or removed or changed:
                    tables_to_update.append(table_name)
                    print(f"[INFO] Table '{table_name}' has structural changes:")
                    if added:
                        print(f"  - Added columns: {', '.join(added)}")
                    if removed:
                        print(f"  - Removed columns: {', '.join(removed)}")
                    if changed:
                        print(f"  - Changed columns: {', '.join(changed)}")
                    print("")
        
        if new_tables:
            print(f"[INFO] New tables to create: {', '.join(new_tables)}")
            print("")
        
        if not new_tables and not tables_to_update:
            print("[INFO] No changes detected in database schema")
            print("")
        
        # Drop and recreate tables that need updates
        if tables_to_update:
            print(f"[WARNING] Dropping and recreating tables: {', '.join(tables_to_update)}")
            print("[WARNING] This will DELETE ALL DATA in these tables!")
            print("")
            
            for table_name in tables_to_update:
                print(f"[INFO] Dropping table '{table_name}'...")
                model_tables[table_name].drop(db.engine, checkfirst=True)
            
            print("")
        
        # Create all tables (creates new ones and recreates dropped ones)
        print("[INFO] Creating/updating tables...")
        db.create_all()
        
        print("[SUCCESS] Database schema updated successfully!")
        print("")
        
        # Show updated table list
        inspector = inspect(db.engine)
        updated_tables = inspector.get_table_names()
        print(f"[INFO] Current tables in database: {', '.join(updated_tables)}")
        
except Exception as e:
    print(f"\n[ERROR] Failed to update database: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF
RESULT=$?

echo ""
if [ $RESULT -eq 0 ]; then
    echo "==================================="
    echo "Database update complete!"
    echo "==================================="
else
    exit $RESULT
fi
