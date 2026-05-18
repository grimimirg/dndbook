"""Add user profile fields

Revision ID: f31993015ef0
Revises: 
Create Date: 2026-05-16

"""
from alembic import op
import sqlalchemy as sa


revision = 'f31993015ef0'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add nickname column if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'nickname'
            ) THEN
                ALTER TABLE users ADD COLUMN nickname VARCHAR(80);
            END IF;
        END $$;
    """)

    # Add biography column if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'biography'
            ) THEN
                ALTER TABLE users ADD COLUMN biography TEXT;
            END IF;
        END $$;
    """)

    # Add avatar_url column if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'avatar_url'
            ) THEN
                ALTER TABLE users ADD COLUMN avatar_url VARCHAR(500);
            END IF;
        END $$;
    """)


def downgrade():
    # Remove the columns
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'nickname'
            ) THEN
                ALTER TABLE users DROP COLUMN nickname;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'biography'
            ) THEN
                ALTER TABLE users DROP COLUMN biography;
            END IF;
        END $$;
    """)

    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'avatar_url'
            ) THEN
                ALTER TABLE users DROP COLUMN avatar_url;
            END IF;
        END $$;
    """)
