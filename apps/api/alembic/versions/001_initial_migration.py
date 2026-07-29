"""initial migration: users and projects

Revision ID: 001
Revises:
Create Date: 2026-07-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('avatar_url', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_users_email', 'users', ['email'])

    op.create_table(
        'projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(255), nullable=False, server_default='Untitled Project'),
        sa.Column('floor_plan_graph', JSONB, nullable=True),
        sa.Column('room_styles', JSONB, nullable=True, server_default='{}'),
        sa.Column('thumbnail_url', sa.Text, nullable=True),
        sa.Column('source_image_url', sa.Text, nullable=True),
        sa.Column('width_mm', sa.Float, nullable=True),
        sa.Column('height_mm', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_projects_user_id', 'projects', ['user_id'])

    op.create_table(
        'design_presets',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('room_type', sa.String(50), nullable=False),
        sa.Column('style', sa.String(50), nullable=False),
        sa.Column('preset_data', JSONB, nullable=False),
        sa.Column('is_built_in', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('user_id', sa.String(36), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index('idx_presets_room_style', 'design_presets', ['room_type', 'style'])

    op.create_table(
        'jobs',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='SET NULL'), nullable=True),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='queued'),
        sa.Column('progress', sa.Float, nullable=False, server_default='0'),
        sa.Column('result_url', sa.Text, nullable=True),
        sa.Column('error_message', sa.Text, nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('jobs')
    op.drop_table('design_presets')
    op.drop_table('projects')
    op.drop_table('users')
