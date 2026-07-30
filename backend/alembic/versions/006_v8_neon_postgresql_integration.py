"""v8 neon postgresql integration migration

Revision ID: 006_v8_neon_postgresql_integration
Revises: 005_v6_enterprise_broadcast_engine
Create Date: 2026-07-30 15:45:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '006_v8_neon_postgresql'
down_revision = '005_v6_broadcast_engine'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('dead_letter_jobs'):
        op.create_table(
            'dead_letter_jobs',
            sa.Column('job_id', sa.String(length=36), nullable=False, primary_key=True),
            sa.Column('job_type', sa.String(length=50), nullable=False),
            sa.Column('entity_id', sa.String(length=36), nullable=False),
            sa.Column('temple_id', sa.String(length=36), nullable=False, server_default='SKSA_MAIN'),
            sa.Column('payload_json', sa.Text(), nullable=True),
            sa.Column('failure_reason', sa.Text(), nullable=False),
            sa.Column('stack_trace', sa.Text(), nullable=True),
            sa.Column('attempts_count', sa.Integer(), server_default='1', nullable=False),
            sa.Column('status', sa.String(length=20), server_default='UNRESOLVED', nullable=False),
            sa.Column('failed_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('reprocessed_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('reprocessed_by', sa.String(length=36), nullable=True),
        )
        op.create_index('idx_dead_letter_job_type', 'dead_letter_jobs', ['job_type'])
        op.create_index('idx_dead_letter_entity_id', 'dead_letter_jobs', ['entity_id'])
        op.create_index('idx_dead_letter_temple_id', 'dead_letter_jobs', ['temple_id'])
        op.create_index('idx_dead_letter_status', 'dead_letter_jobs', ['status'])


def downgrade():
    op.drop_table('dead_letter_jobs')
