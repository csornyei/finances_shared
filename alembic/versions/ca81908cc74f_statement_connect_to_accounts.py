"""statement connect to accounts

Revision ID: ca81908cc74f
Revises: 0485b5168517
Create Date: 2025-06-21 08:20:19.595875

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ca81908cc74f"
down_revision: Union[str, None] = "0485b5168517"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "statements",
        sa.Column("account_name", sa.String(), nullable=False, server_default=""),
    )

    op.alter_column(
        "statements",
        "account",
        existing_type=sa.String(),
        nullable=False,
        existing_nullable=False,
        server_default=None,
        new_column_name="account_iban",
    )

    op.create_foreign_key(
        "fk_statements_source_account",
        "statements",
        "accounts",
        ["account_iban", "account_name"],
        ["iban", "name"],
    )

    op.create_foreign_key(
        "fk_statements_destination_account",
        "statements",
        "accounts",
        ["counterparty_iban", "counterparty_name"],
        ["iban", "name"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "fk_statements_destination_account", "statements", type_="foreignkey"
    )
    op.drop_constraint("fk_statements_source_account", "statements", type_="foreignkey")

    op.alter_column(
        "statements",
        "account_iban",
        existing_type=sa.String(),
        nullable=False,
        existing_nullable=False,
        server_default=None,
        new_column_name="account",
    )
    op.drop_column("statements", "account_name")
