"""Payment processing service."""

import logging
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.order import Order, OrderStatus

logger = logging.getLogger(__name__)


async def process_payment(
    db: AsyncSession,
    order_id: int,
    amount: Decimal,
) -> bool:
    """
    Simulate payment processing for an order.

    Args:
        db: Database session.
        order_id: ID of the order.
        amount: Amount to charge.

    Returns:
        True if payment succeeded, False otherwise.
    """
    # In a real system, integrate with payment gateway here.
    # For demo, we simulate success if amount > 0.
    if amount <= 0:
        logger.warning(f"Invalid payment amount {amount} for order {order_id}")
        return False

    # Simulate external call success
    logger.info(f"Payment of {amount} processed for order {order_id}")

    # Update order status to PAID
    order = await db.get(Order, order_id)
    if order and order.status == OrderStatus.RESERVED:
        order.status = OrderStatus.PAID
        await db.commit()
        logger.info(f"Order {order_id} marked as PAID")
        return True

    logger.error(f"Order {order_id} not in RESERVED state, cannot update to PAID")
    return False
