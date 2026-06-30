"""Add notes table

Revision ID: 20260630_add_notes_table
Revises: 20260516_add_character_mentions
Create Date: 2026-06-30

"""
from alembic import op
import sqlalchemy as sa


revision = '20260630_add_notes_table'
down_revision = '20260516_add_character_mentions'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title VARCHAR(200) NOT NULL,
            content TEXT NOT NULL DEFAULT '',
            owner_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            visibility VARCHAR(20) NOT NULL DEFAULT 'private',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            parent_id INTEGER REFERENCES notes(id) ON DELETE CASCADE
        );
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_notes_owner_id ON notes(owner_id);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_notes_visibility ON notes(visibility);
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_notes_parent_id ON notes(parent_id);
    """)


def downgrade():
    op.execute("DROP INDEX IF EXISTS idx_notes_parent_id;")
    op.execute("DROP INDEX IF EXISTS idx_notes_visibility;")
    op.execute("DROP INDEX IF EXISTS idx_notes_owner_id;")
    op.execute("DROP TABLE IF EXISTS notes;")
