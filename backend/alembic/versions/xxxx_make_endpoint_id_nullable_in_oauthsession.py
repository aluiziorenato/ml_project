"""Make endpoint_id nullable in oauthsession

Revision ID: abcdef123456
Revises: <revision_anterior>
Create Date: 2025-08-11 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'abcdef123456'   # substitua pelo id gerado
down_revision = '<revision_anterior>'  # mantenha o id da revisão anterior
branch_labels = None
depends_on = None


def upgrade():
    # Alterar coluna para aceitar NULL
    op.alter_column('oauthsession', 'endpoint_id',
               existing_type=sa.INTEGER(),
               nullable=True)


def downgrade():
    # Voltar para NOT NULL caso precise reverter
    op.alter_column('oauthsession', 'endpoint_id',
               existing_type=sa.INTEGER(),
               nullable=False)
