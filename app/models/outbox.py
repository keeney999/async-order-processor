"""Transactional outbox table."""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import func
from sqlmodel import Field, SQLModel


class OutboxStatus(str, Enum):
    """Status of outbox message."""

    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class Outbox(SQLModel, table=True):
    """Outbox table for reliable event publishing."""

    id: Optional[int] = Field(default=None, primary_key=True)
    event_type: str = Field(index=True, max_length=255)
    payload: str
    status: OutboxStatus = Field(default=OutboxStatus.PENDING, index=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"server_default": func.now()}
    )
    processed_at: Optional[datetime] = None
    retries: int = Field(default=0)
    last_error: Optional[str] = Field(default=None, max_length=500)
