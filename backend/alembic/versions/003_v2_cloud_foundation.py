"""v2 cloud foundation schema migration

Revision ID: 003_v2_cloud_foundation
Revises: 002_communication_settings
Create Date: 2026-07-30 11:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '003_v2_cloud_foundation'
down_revision = '002_communication_settings'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Persons Table
    if not inspector.has_table('persons'):
        op.create_table(
            'persons',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('temple_id', sa.String(length=36), nullable=True),
            sa.Column('name', sa.String(length=150), nullable=False),
            sa.Column('phone', sa.String(length=20), nullable=False),
            sa.Column('village', sa.String(length=100), nullable=False),
            sa.Column('address', sa.Text(), nullable=True),
            sa.Column('first_visit', sa.String(length=50), nullable=False),
            sa.Column('last_visit', sa.String(length=50), nullable=False),
            sa.Column('total_visits', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_by', sa.String(length=36), nullable=True),
            sa.Column('updated_by', sa.String(length=36), nullable=True),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('phone')
        )
        op.create_index('idx_persons_phone', 'persons', ['phone'])
        op.create_index('idx_persons_temple', 'persons', ['temple_id'])

    # 2. Sync Tokens Table
    if not inspector.has_table('sync_tokens'):
        op.create_table(
            'sync_tokens',
            sa.Column('id', sa.String(length=36), nullable=False),
            sa.Column('temple_id', sa.String(length=36), nullable=False),
            sa.Column('client_id', sa.String(length=100), nullable=False),
            sa.Column('device_name', sa.String(length=100), nullable=True),
            sa.Column('last_synced_token', sa.String(length=100), nullable=True),
            sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_by', sa.String(length=36), nullable=True),
            sa.Column('updated_by', sa.String(length=36), nullable=True),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index('idx_sync_tokens_client', 'sync_tokens', ['client_id'])


def downgrade():
    op.drop_table('sync_tokens')
    op.drop_table('persons')
