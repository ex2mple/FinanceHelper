"""Fix issues with User Model

Revision ID: 7ea345582030
Revises: efa4571dc6cc
Create Date: 2025-04-12 07:53:38.882758

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ea345582030'
down_revision: Union[str, None] = 'efa4571dc6cc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
