"""Product model."""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlmodel import Field, SQLModel


class Product(SQLModel, table=True):
    """Product available for purchase."""

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    price: Decimal = Field(max_digits=10, decimal_places=2)
    stock: int = Field(default=0, ge=0)
    created_at: datetime = Field(default_factory=datetime.now())
    updated_at: datetime = Field(
        default_factory=datetime.now(),
        sa_column_kwargs={"onupdate": datetime.now()},
    )
