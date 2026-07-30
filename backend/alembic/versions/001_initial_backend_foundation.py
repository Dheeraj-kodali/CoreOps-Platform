"""Initial backend foundation schema with 19 entities and UUID primary keys

Revision ID: 001_initial_backend_foundation
Revises: 
Create Date: 2026-07-26 16:10:00.000000

"""
from alembic import op
import sqlalchemy as sa
import app.models
from app.core.database import Base

# revision identifiers, used by Alembic.
revision = '001_initial_backend_foundation'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
