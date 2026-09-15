"""initial schema

Revision ID: 0001_initial
Revises:
Create Date: 2026-09-13

Creates every table from the current SQLAlchemy models in one shot.
This is a pragmatic starting point for a brand-new database — it uses
Base.metadata directly rather than hand-written op.create_table() calls,
since there's no prior schema to diff against yet.

Once this migration has been applied to a real database, generate all
FUTURE migrations the normal way:

    alembic revision --autogenerate -m "add reliability_notes to farmers"

Autogenerate needs a live DB connection to diff against, which is why
this first one is written by hand instead.
"""
from alembic import op

from app.models.base import Base
import app.models  # noqa: F401 — registers every model on Base.metadata

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
