"""Order schemas for request/response."""

from typing import List

from pydantic import BaseModel


class OrderItemCreate(BaseModel):
    """Item in order creation request."""

    product_id: int
    quantity: int


class OrderCreate(BaseModel):
    """Order creation request."""

    user_id: int
    items: List[OrderItemCreate]
