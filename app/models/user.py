"""User model."""

from datetime import datetime
from typing import Optional

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    """User account table."""

    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True, max_length=100)
    full_name: str = Field(max_length=100)
    hashed_password: str
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.now())
    updated_at: datetime = Field(
        default_factory=datetime.now(),
        sa_column_kwargs={"onupdate": datetime.now()},
    )
