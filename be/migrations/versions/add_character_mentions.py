"""Add character mentions table

Revision ID: 20260516_add_character_mentions
Revises: add_user_profile_fields
Create Date: 2026-05-16

"""
from alembic import op
import sqlalchemy as sa


revision = '20260516_add_character_mentions'
down_revision = 'add_user_profile_fields'
branch_labels = None
depends_on = None


def upgrade():
    # Create character_mentions table
    op.execute("""
        CREATE TABLE IF NOT EXISTS character_mentions (
            id SERIAL PRIMARY KEY,
            post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
            character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
            mention_text VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Create index on post_id for faster lookups
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_character_mentions_post_id ON character_mentions(post_id);
    """)

    # Create index on character_id for faster lookups
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_character_mentions_character_id ON character_mentions(character_id);
    """)


def downgrade():
    # Drop the indexes
    op.execute("""
        DROP INDEX IF EXISTS idx_character_mentions_post_id;
    """)

    op.execute("""
        DROP INDEX IF EXISTS idx_character_mentions_character_id;
    """)

    # Drop the table
    op.execute("""
        DROP TABLE IF EXISTS character_mentions;
    """)
