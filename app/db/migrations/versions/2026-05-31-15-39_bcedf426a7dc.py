"""Initial migration.

Revision ID: bcedf426a7dc
Revises:
Create Date: 2026-05-31 15:39:26.787964

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "bcedf426a7dc"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""


def downgrade() -> None:
    """Downgrade schema."""
