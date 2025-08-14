"""create oauth_tokens table linked to users

Revision ID: create_oauth_tokens_table
Revises: 
Create Date: 2025-08-12 23:10:00.000000
"""
from alembic import op
import sqlalchemy as sa

# Revision identifiers
revision = 'create_oauth_tokens_table'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'oauth_tokens',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('access_token', sa.String(), nullable=False),
        sa.Column('refresh_token', sa.String(), nullable=True),
        sa.Column('token_type', sa.String(), nullable=True),
        sa.Column('scope', sa.String(), nullable=True),
        sa.Column('expires_in', sa.Integer(), nullable=True),
        sa.Column('obtained_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table('oauth_tokens')
