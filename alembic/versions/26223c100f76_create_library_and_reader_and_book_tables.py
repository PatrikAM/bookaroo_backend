"""create library and reader and book tables

Revision ID: 26223c100f76
Revises: 
Create Date: 2025-04-24 10:20:33.270351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26223c100f76'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        'reader',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String, nullable=True),
        sa.Column('surname', sa.String, nullable=True),
        sa.Column('sex', sa.String, nullable=True),
        sa.Column('email', sa.String, nullable=True),
    )

    op.create_table(
        'library',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('address', sa.String, nullable=True),
        sa.Column('floor', sa.String, nullable=True),
        sa.Column('name', sa.Integer, nullable=False),
    )

    op.create_table(
        'book',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('title', sa.String, nullable=False),
        sa.Column('series', sa.String, nullable=True),
        sa.Column('author', sa.String, nullable=True),
        sa.Column('binding', sa.String, nullable=True),
        sa.Column('cover_image', sa.String, nullable=True),
        sa.Column('reader_id', sa.Integer, sa.ForeignKey('reader.id'), nullable=True),
        sa.Column('publisher', sa.String, nullable=True),
        sa.Column('published', sa.Integer, nullable=True),
        sa.Column('isbn', sa.String, nullable=True),
        sa.Column('borrower_id', sa.Integer, sa.ForeignKey('reader.id'), nullable=True),
        sa.Column('library_id', sa.Integer, sa.ForeignKey('library.id'),
                  nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('reader')
    op.drop_table('book')
    op.drop_table('library')
