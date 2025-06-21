import uuid
from datetime import datetime

from sqlalchemy import TIMESTAMP, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .account import Account
from .base import Base


class Statements(Base):
    __tablename__ = "statements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    date: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    interest_date: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    amount: Mapped[int] = mapped_column(nullable=False)
    account_iban: Mapped[str] = mapped_column(nullable=False)
    account_name: Mapped[str] = mapped_column(nullable=False, default="")
    counterparty_iban: Mapped[str | None] = mapped_column(nullable=True)
    counterparty_name: Mapped[str | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)

    source_account: Mapped["Account"] = relationship(
        "Account",
        primaryjoin="and_(Statements.account_iban == foreign(Account.iban), Statements.account_name == foreign(Account.name))",
        foreign_keys=[account_iban, account_name],
        viewonly=True,
    )

    destination_account: Mapped["Account"] = relationship(
        "Account",
        primaryjoin="and_(Statements.counterparty_iban == Account.iban, Statements.counterparty_name == Account.name)",
        foreign_keys=[counterparty_iban, counterparty_name],
        viewonly=True,
    )

    __table_args__ = (
        ForeignKeyConstraint(
            ["account_iban", "account_name"],
            ["accounts.iban", "accounts.name"],
            name="fk_statements_source_account",
        ),
        ForeignKeyConstraint(
            ["counterparty_iban", "counterparty_name"],
            ["accounts.iban", "accounts.name"],
            name="fk_statements_destination_account",
        ),
    )
