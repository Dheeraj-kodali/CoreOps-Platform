"""v4 immutable enterprise audit system migration

Revision ID: 004_v4_immutable_audit_system
Revises: 003_v2_cloud_foundation
Create Date: 2026-07-30 11:50:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '004_v4_immutable_audit_system'
down_revision = '003_v2_cloud_foundation'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if inspector.has_table('audit_logs'):
        columns = [col['name'] for col in inspector.get_columns('audit_logs')]
        with op.batch_alter_table('audit_logs') as batch_op:
            if 'audit_id' not in columns:
                batch_op.add_column(sa.Column('audit_id', sa.String(length=36), nullable=True))
            if 'trace_id' not in columns:
                batch_op.add_column(sa.Column('trace_id', sa.String(length=36), nullable=True))
            if 'temple_id' not in columns:
                batch_op.add_column(sa.Column('temple_id', sa.String(length=36), nullable=True))
            if 'role' not in columns:
                batch_op.add_column(sa.Column('role', sa.String(length=50), nullable=True))
            if 'device_id' not in columns:
                batch_op.add_column(sa.Column('device_id', sa.String(length=100), nullable=True))
            if 'session_id' not in columns:
                batch_op.add_column(sa.Column('session_id', sa.String(length=100), nullable=True))
            if 'entity_type' not in columns:
                batch_op.add_column(sa.Column('entity_type', sa.String(length=50), nullable=True))
            if 'entity_id' not in columns:
                batch_op.add_column(sa.Column('entity_id', sa.String(length=36), nullable=True))
            if 'old_value' not in columns:
                batch_op.add_column(sa.Column('old_value', sa.Text(), nullable=True))
            if 'new_value' not in columns:
                batch_op.add_column(sa.Column('new_value', sa.Text(), nullable=True))
            if 'status' not in columns:
                batch_op.add_column(sa.Column('status', sa.String(length=20), server_default='SUCCESS', nullable=True))
            if 'severity' not in columns:
                batch_op.add_column(sa.Column('severity', sa.String(length=20), server_default='INFO', nullable=True))
            if 'timestamp' not in columns:
                batch_op.add_column(sa.Column('timestamp', sa.DateTime(timezone=True), nullable=True))
            if 'application_version' not in columns:
                batch_op.add_column(sa.Column('application_version', sa.String(length=20), server_default='2.0.0', nullable=True))
            if 'platform' not in columns:
                batch_op.add_column(sa.Column('platform', sa.String(length=50), server_default='Backend-FastAPI', nullable=True))
            if 'api_version' not in columns:
                batch_op.add_column(sa.Column('api_version', sa.String(length=20), server_default='v2.0', nullable=True))
            if 'duration_ms' not in columns:
                batch_op.add_column(sa.Column('duration_ms', sa.Float(), server_default='0.0', nullable=True))

        indexes = [idx['name'] for idx in inspector.get_indexes('audit_logs')]
        if 'idx_audit_temple_timestamp' not in indexes:
            op.create_index('idx_audit_temple_timestamp', 'audit_logs', ['temple_id', 'timestamp'])
        if 'idx_audit_action' not in indexes:
            op.create_index('idx_audit_action', 'audit_logs', ['action'])
        if 'idx_audit_severity' not in indexes:
            op.create_index('idx_audit_severity', 'audit_logs', ['severity'])
        if 'idx_audit_trace' not in indexes:
            op.create_index('idx_audit_trace', 'audit_logs', ['trace_id'])


def downgrade():
    op.drop_index('idx_audit_trace', table_name='audit_logs')
    op.drop_index('idx_audit_severity', table_name='audit_logs')
    op.drop_index('idx_audit_action', table_name='audit_logs')
    op.drop_index('idx_audit_temple_timestamp', table_name='audit_logs')
