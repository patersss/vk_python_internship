import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import text, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Environment(str, Enum):
    PROD = "prod",
    PREPROD = "preprod",
    STAGE = "stage"


class Domain(str, Enum):
    CANARY = "canary",
    REGULAR = "regular"


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("now()")
    )

    login: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True
    )

    password: Mapped[str] = mapped_column(
        String(255)
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True)
    )

    env: Mapped[Environment]

    domain: Mapped[Domain]

    locktime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=None,
        nullable=True
    )