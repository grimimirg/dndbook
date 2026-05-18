"""Add related_invite_id to notifications

Revision ID: c674070d201e
Revises: add_user_profile_fields
Create Date: 2026-05-17

"""
from alembic import op
import sqlalchemy as sa


revision = 'c674070d201e'
down_revision = 'f31993015ef0'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'notifications' AND column_name = 'related_invite_id'
            ) THEN
                ALTER TABLE notifications
                    ADD COLUMN related_invite_id INTEGER
                    REFERENCES campaign_invites(id) ON DELETE CASCADE;
            END IF;
        END $$;
    """)


def downgrade():
    op.execute("""
        ALTER TABLE notifications DROP COLUMN IF EXISTS related_invite_id;
    """)
