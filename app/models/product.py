"""Product model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import func
from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    """Product available for purchase."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": func.now()}
    )
