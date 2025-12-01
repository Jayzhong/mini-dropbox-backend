"""add share_links table

Revision ID: 20251201_add_share_links
Revises: 2724dd206941
Create Date: 2025-12-01
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251201_add_share_links'
down_revision = '2724dd206941'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'share_links',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('token', sa.String(length=128), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_disabled', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('token', name='uq_sharelink_token'),
    )
    op.create_index('ix_sharelink_file_id', 'share_links', ['file_id'], unique=False)
    op.create_index(op.f('ix_share_links_token'), 'share_links', ['token'], unique=False)
    op.create_foreign_key('fk_share_links_file', 'share_links', 'files', ['file_id'], ['id'])
    op.create_foreign_key('fk_share_links_user', 'share_links', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    op.drop_constraint('fk_share_links_file', 'share_links', type_='foreignkey')
    op.drop_constraint('fk_share_links_user', 'share_links', type_='foreignkey')
    op.drop_index('ix_sharelink_file_id', table_name='share_links')
    op.drop_index(op.f('ix_share_links_token'), table_name='share_links')
    op.drop_table('share_links')
