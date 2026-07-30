"""v6 enterprise broadcast messaging engine migration

Revision ID: 005_v6_enterprise_broadcast_engine
Revises: 004_v4_immutable_audit_system
Create Date: 2026-07-30 12:55:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_v6_broadcast_engine'
down_revision = '004_v4_immutable_audit_system'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    # 1. Create broadcast_campaigns table
    if not inspector.has_table('broadcast_campaigns'):
        op.create_table(
            'broadcast_campaigns',
            sa.Column('campaign_id', sa.String(length=36), nullable=False, primary_key=True),
            sa.Column('temple_id', sa.String(length=36), nullable=False),
            sa.Column('title', sa.String(length=150), nullable=False),
            sa.Column('description', sa.Text(), nullable=True),
            sa.Column('template_id', sa.String(length=50), nullable=True),
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('status', sa.String(length=20), server_default='DRAFT', nullable=False),
            sa.Column('created_by', sa.String(length=36), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('total_recipients', sa.Integer(), server_default='0', nullable=False),
            sa.Column('queued_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('sent_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('delivered_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('failed_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('cancelled_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('audience_filter_json', sa.Text(), nullable=True),
        )
        op.create_index('idx_broadcast_temple_status', 'broadcast_campaigns', ['temple_id', 'status'])
        op.create_index('idx_broadcast_scheduled_at', 'broadcast_campaigns', ['scheduled_at'])

    # 2. Create broadcast_recipients table
    if not inspector.has_table('broadcast_recipients'):
        op.create_table(
            'broadcast_recipients',
            sa.Column('recipient_id', sa.String(length=36), nullable=False, primary_key=True),
            sa.Column('campaign_id', sa.String(length=36), sa.ForeignKey('broadcast_campaigns.campaign_id', ondelete='CASCADE'), nullable=False),
            sa.Column('temple_id', sa.String(length=36), nullable=False),
            sa.Column('person_uuid', sa.String(length=36), nullable=True),
            sa.Column('mobile_number', sa.String(length=20), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=True),
            sa.Column('status', sa.String(length=20), server_default='QUEUED', nullable=False),
            sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('error_message', sa.Text(), nullable=True),
        )
        op.create_index('idx_recipient_campaign_status', 'broadcast_recipients', ['campaign_id', 'status'])
        op.create_index('idx_recipient_person', 'broadcast_recipients', ['person_uuid'])


def downgrade():
    op.drop_table('broadcast_recipients')
    op.drop_table('broadcast_campaigns')
