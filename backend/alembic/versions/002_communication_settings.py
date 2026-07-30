"""Add communication_settings, message_templates, and communication_history_v2 tables

Revision ID: 002_communication_settings
Revises: 001_initial_backend_foundation
Create Date: 2026-07-28 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002_communication_settings'
down_revision = '001_initial_backend_foundation'
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('communication_settings'):
        op.create_table(
            'communication_settings',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('mode', sa.String(20), nullable=False, default='DISABLED', index=True),
            sa.Column('access_token', sa.Text, nullable=True),
            sa.Column('phone_number_id', sa.String(50), nullable=True),
            sa.Column('business_account_id', sa.String(50), nullable=True),
            sa.Column('verify_token', sa.String(100), nullable=True),
            sa.Column('auto_send', sa.Boolean, nullable=False, default=False),
            sa.Column('allow_edit', sa.Boolean, nullable=False, default=False),
            sa.Column('save_history', sa.Boolean, nullable=False, default=True),
            sa.Column('retry_failed', sa.Boolean, nullable=False, default=False),
            sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_by', sa.String(36), nullable=True),
            sa.Column('updated_by', sa.String(36), nullable=True),
        )

    if not inspector.has_table('message_templates'):
        op.create_table(
            'message_templates',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('template_type', sa.String(20), nullable=False, unique=True, index=True),
            sa.Column('title', sa.String(200), nullable=False),
            sa.Column('message', sa.Text, nullable=False),
            sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_by', sa.String(36), nullable=True),
            sa.Column('updated_by', sa.String(36), nullable=True),
        )

    if not inspector.has_table('communication_history_v2'):
        op.create_table(
            'communication_history_v2',
            sa.Column('id', sa.String(36), primary_key=True),
            sa.Column('visitor_id', sa.String(36), nullable=True, index=True),
            sa.Column('phone', sa.String(20), nullable=False, index=True),
            sa.Column('message', sa.Text, nullable=False),
            sa.Column('message_type', sa.String(20), nullable=False, index=True),
            sa.Column('status', sa.String(20), nullable=False, default='PENDING', index=True),
            sa.Column('meta_message_id', sa.String(100), nullable=True),
            sa.Column('error_message', sa.Text, nullable=True),
            sa.Column('is_deleted', sa.Boolean, nullable=False, default=False),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_by', sa.String(36), nullable=True),
            sa.Column('updated_by', sa.String(36), nullable=True),
        )


def downgrade() -> None:
    op.drop_table('communication_history_v2')
    op.drop_table('message_templates')
    op.drop_table('communication_settings')
