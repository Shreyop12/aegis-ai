import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.base import Base


class Trace(Base):
    __tablename__ = "traces"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    application: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    environment: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    user_input: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    prompt: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    model_output: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )