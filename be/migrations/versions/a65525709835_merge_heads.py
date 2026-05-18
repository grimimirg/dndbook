"""merge_heads

Revision ID: a65525709835
Revises: 20260516_add_character_mentions, add_related_invite_id_to_notifications
Create Date: 2026-05-17 18:51:35.698928

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a65525709835'
down_revision = ('ba8f362d619f', 'c674070d201e')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
