import uuid
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Statements(Base):
    __tablename__ = "statements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    date: Mapped[datetime] = mapped_column(nullable=False)
    interest_date: Mapped[datetime] = mapped_column(nullable=False)
    amount: Mapped[int] = mapped_column(nullable=False)
    account: Mapped[str] = mapped_column(nullable=False)
    counterparty_iban: Mapped[str | None] = mapped_column(nullable=True)
    counterparty_name: Mapped[str | None] = mapped_column(nullable=True)
    description: Mapped[str | None] = mapped_column(nullable=True)
