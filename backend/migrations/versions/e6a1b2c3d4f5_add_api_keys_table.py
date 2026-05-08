"""add api keys table

Revision ID: e6a1b2c3d4f5
Revises: a1b2c3d4e5f7
Create Date: 2026-05-08 18:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'e6a1b2c3d4f5'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'api_keys',
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('key_id', sa.String(length=64), nullable=False),
        sa.Column('key_hash', sa.String(length=128), nullable=False),
        sa.Column('last4', sa.String(length=4), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ['user_id'],
            ['users.id'],
            name='fk_api_keys_user_id',
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name='pk_api_keys'),
        sa.UniqueConstraint('key_id', name='uq_api_keys_key_id'),
    )
    op.create_index('idx_api_keys_user_id', 'api_keys', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_api_keys_user_id', table_name='api_keys')
    op.drop_table('api_keys')
