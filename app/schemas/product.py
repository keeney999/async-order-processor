"""Pydantic schemas for Product."""

from decimal import Decimal

from pydantic import BaseModel


class ProductBase(BaseModel):
    """Base product schema."""

    name: str
    description: str | None = None
    price: Decimal
    stock: int


class ProductCreate(ProductBase):
    """Schema for creating a new product."""


class ProductResponse(ProductBase):
    """Schema for product response."""

    id: int

    class Config:
        from_attributes = True
