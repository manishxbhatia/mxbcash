"""Initial schema

Revision ID: 0001
Revises:
Create Date: 2026-02-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "commodities",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("mnemonic", sa.String(16), nullable=False, unique=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("fraction", sa.Integer, nullable=False, default=100),
    )

    op.create_table(
        "prices",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("commodity_id", sa.Integer, sa.ForeignKey("commodities.id"), nullable=False),
        sa.Column("currency_id", sa.Integer, sa.ForeignKey("commodities.id"), nullable=False),
        sa.Column("numerator", sa.Integer, nullable=False),
        sa.Column("denominator", sa.Integer, nullable=False, default=1),
        sa.Column("source", sa.String(16), nullable=False, default="user"),
    )

    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("full_name", sa.String(512), nullable=False),
        sa.Column("account_type", sa.Enum("ASSET", "LIABILITY", "EQUITY", "INCOME", "EXPENSE", name="accounttype"), nullable=False),
        sa.Column("description", sa.String(512), nullable=True),
        sa.Column("placeholder", sa.Boolean, nullable=False, default=False),
        sa.Column("commodity_id", sa.Integer, sa.ForeignKey("commodities.id"), nullable=False),
        sa.Column("parent_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=True),
    )

    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("date", sa.Date, nullable=False),
        sa.Column("description", sa.String(256), nullable=False, default=""),
        sa.Column("notes", sa.String(1024), nullable=True),
        sa.Column("import_ref", sa.String(256), nullable=True, unique=True),
        sa.Column("currency_id", sa.Integer, sa.ForeignKey("commodities.id"), nullable=False),
    )

    op.create_table(
        "splits",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("transaction_id", sa.Integer, sa.ForeignKey("transactions.id"), nullable=False),
        sa.Column("account_id", sa.Integer, sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("value_minor", sa.Integer, nullable=False),
        sa.Column("quantity_minor", sa.Integer, nullable=False),
        sa.Column("memo", sa.String(512), nullable=True),
        sa.Column("reconciled", sa.String(1), nullable=False, default="n"),
    )


def downgrade() -> None:
    op.drop_table("splits")
    op.drop_table("transactions")
    op.drop_table("accounts")
    op.drop_table("prices")
    op.drop_table("commodities")
