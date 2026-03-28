"""Order and order item models."""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from sqlalchemy import func
from sqlmodel import Field, Relationship, SQLModel


class OrderStatus(str, Enum):
    """Possible order statuses."""

    PENDING = "pending"
    RESERVED = "reserved"
    PAID = "paid"
    CANCELLED = "cancelled"
    FAILED = "failed"


class Order(SQLModel, table=True):
    """Customer order."""

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    status: OrderStatus = Field(default=OrderStatus.PENDING, index=True)
    total_amount: Optional[Decimal] = Field(
        default=None, max_digits=10, decimal_places=2
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"server_default": func.now()}
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": func.now()}
    )

    items: List["OrderItem"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    """Line item in an order."""

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(ge=1)
    price: Decimal = Field(max_digits=10, decimal_places=2)
    created_at: datetime = Field(
        default_factory=datetime.utcnow, sa_column_kwargs={"server_default": func.now()}
    )

    order: Order = Relationship(back_populates="items")
