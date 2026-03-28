"""Order service with outbox."""

import json
from decimal import Decimal
from typing import List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderItem
from app.models.outbox import Outbox
from app.models.product import Product
from app.schemas.order import OrderCreate


async def create_order_with_outbox(db: AsyncSession, order_data: OrderCreate) -> int:
    """
    Create order and outbox event in a single transaction.

    Args:
        db: Database session.
        order_data: Order data from API.

    Returns:
        ID of created order.

    Raises:
        ValueError: If product does not exist or other validation fails.
    """
    # Fetch all products to validate existence and get prices
    product_ids = [item.product_id for item in order_data.items]
    products = await db.execute(select(Product).where(Product.id.in_(product_ids)))
    products_map = {p.id: p for p in products.scalars().all()}

    # Validate all products exist
    for item in order_data.items:
        if item.product_id not in products_map:
            raise ValueError(f"Product {item.product_id} not found")

    # Create order
    order = Order(user_id=order_data.user_id, status="pending")
    db.add(order)
    await db.flush()  # get order.id

    total = Decimal("0")
    order_items: List[OrderItem] = []
    for item in order_data.items:
        product = products_map[item.product_id]
        price = product.price
        order_item = OrderItem(
            order_id=order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=price,
        )
        order_items.append(order_item)
        db.add(order_item)
        total += price * item.quantity

    order.total_amount = total
    await db.flush()

    # Prepare outbox event
    event_payload = {
        "order_id": order.id,
        "user_id": order.user_id,
        "items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "price": str(item.price),
            }
            for item in order_items
        ],
        "total": str(total),
    }
    outbox = Outbox(
        event_type="order_created",
        payload=json.dumps(event_payload),
    )
    db.add(outbox)

    await db.commit()
    return order.id
