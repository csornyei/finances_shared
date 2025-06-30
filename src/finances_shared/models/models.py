import uuid
from datetime import datetime
from typing import List

from sqlalchemy import (
    TIMESTAMP,
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column, relationship

Base = declarative_base()

tags_to_statement_table = Table(
    "tags_to_statement",
    Base.metadata,
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
    Column("statement_id", ForeignKey("statements.id"), primary_key=True),
)


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    iban: Mapped[str] = mapped_column(String, nullable=False)
    nickname: Mapped[str] = mapped_column(String, nullable=False, unique=True)

    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accounts.id"), nullable=True
    )

    __table_args__ = (UniqueConstraint("name", "iban", name="uq_account_name_iban"),)


class Tags(Base):
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(nullable=False, unique=True)
    color: Mapped[str] = mapped_column(nullable=True)


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
        Account,
        primaryjoin="and_(Statements.account_iban == foreign(Account.iban), Statements.account_name == foreign(Account.name))",
        foreign_keys=[account_iban, account_name],
        viewonly=True,
    )

    destination_account: Mapped["Account"] = relationship(
        Account,
        primaryjoin="and_(Statements.counterparty_iban == Account.iban, Statements.counterparty_name == Account.name)",
        foreign_keys=[counterparty_iban, counterparty_name],
        viewonly=True,
    )

    tags: Mapped[List[Tags]] = relationship(
        Tags,
        secondary=tags_to_statement_table,
        back_populates="statements",
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


Account.parent = relationship(
    "Account",
    remote_side=[Account.id],
    back_populates="aliases",
)

Account.aliases = relationship(
    "Account",
    back_populates="parent",
    foreign_keys=[Account.parent_id],
)

Tags.statements = relationship(
    Statements,
    secondary=tags_to_statement_table,
    back_populates="tags",
)
