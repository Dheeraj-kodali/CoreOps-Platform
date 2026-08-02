"""v10 visitor profiles and visit sessions architecture migration

Revision ID: 007_v10_profiles_and_sessions
Revises: 006_v8_neon_postgresql
Create Date: 2026-08-02 22:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = '007_v10_profiles_and_sessions'
down_revision = '006_v8_neon_postgresql'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table('visitor_profiles'):
        op.create_table(
            'visitor_profiles',
            sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
            sa.Column('visitor_id', sa.String(length=50), nullable=False, unique=True),
            sa.Column('name', sa.String(length=150), nullable=False),
            sa.Column('phone_number', sa.String(length=20), nullable=False, unique=True),
            sa.Column('village_id', sa.String(length=36), sa.ForeignKey('villages.id'), nullable=True),
            sa.Column('village_name_custom', sa.String(length=150), nullable=True),
            sa.Column('gender', sa.String(length=10), nullable=False, server_default='MALE'),
            sa.Column('age', sa.Integer(), nullable=False, server_default='30'),
            sa.Column('default_purpose_id', sa.String(length=36), sa.ForeignKey('purposes.id'), nullable=True),
            sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_by', sa.String(length=36), nullable=True),
            sa.Column('updated_by', sa.String(length=36), nullable=True),
        )
        op.create_index('idx_visitor_profiles_visitor_id', 'visitor_profiles', ['visitor_id'])
        op.create_index('idx_visitor_profiles_phone', 'visitor_profiles', ['phone_number'])
        op.create_index('idx_visitor_profiles_name', 'visitor_profiles', ['name'])

    if not inspector.has_table('visit_sessions'):
        op.create_table(
            'visit_sessions',
            sa.Column('id', sa.String(length=36), nullable=False, primary_key=True),
            sa.Column('visitor_profile_id', sa.String(length=36), sa.ForeignKey('visitor_profiles.id'), nullable=False),
            sa.Column('temple_id', sa.String(length=36), sa.ForeignKey('temples.id'), nullable=True),
            sa.Column('visit_date', sa.Date(), nullable=False),
            sa.Column('check_in_time', sa.Time(), nullable=False),
            sa.Column('check_out_time', sa.Time(), nullable=True),
            sa.Column('persons_count', sa.Integer(), nullable=False, server_default='1'),
            sa.Column('purpose_id', sa.String(length=36), sa.ForeignKey('purposes.id'), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('volunteer_id', sa.String(length=36), sa.ForeignKey('users.id'), nullable=False),
            sa.Column('latitude', sa.Float(), nullable=True),
            sa.Column('longitude', sa.Float(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='INSIDE'),
            sa.Column('sync_status', sa.String(length=20), nullable=False, server_default='SYNCED'),
            sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.text('false')),
            sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('created_by', sa.String(length=36), nullable=True),
            sa.Column('updated_by', sa.String(length=36), nullable=True),
        )
        op.create_index('idx_visit_sessions_profile_id', 'visit_sessions', ['visitor_profile_id'])
        op.create_index('idx_visit_sessions_visit_date', 'visit_sessions', ['visit_date'])
        op.create_index('idx_visit_sessions_status', 'visit_sessions', ['status'])
        op.create_index('idx_visit_sessions_purpose_id', 'visit_sessions', ['purpose_id'])
        op.create_index('idx_visit_sessions_volunteer_id', 'visit_sessions', ['volunteer_id'])


def downgrade():
    op.drop_table('visit_sessions')
    op.drop_table('visitor_profiles')
