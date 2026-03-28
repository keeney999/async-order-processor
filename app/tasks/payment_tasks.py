"""Celery tasks for payment processing."""

import asyncio
import logging

from app.celery import celery_app
from app.core.database import async_session
from app.models.order import Order, OrderStatus
from app.services.payment_service import process_payment

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_payment_task(self, order_id: int) -> dict:
    """
    Celery task to process payment for an order.

    Args:
        order_id: ID of the order.

    Returns:
        Dict with result status.
    """
    logger.info(f"Processing payment for order {order_id}")

    async def _process():
        async with async_session() as db:
            order = await db.get(Order, order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                return {"error": "Order not found"}

            if order.status != OrderStatus.RESERVED:
                logger.warning(
                    f"Order {order_id} status {order.status}, cannot process payment"
                )
                return {"status": order.status.value, "order_id": order_id}

            amount = order.total_amount or 0
            success = await process_payment(db, order_id, amount)
            if success:
                return {"status": "paid", "order_id": order_id}
            else:
                # Optionally, mark order as failed after payment failure
                order.status = OrderStatus.FAILED
                await db.commit()
                return {"error": "Payment failed", "order_id": order_id}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_process())
    finally:
        loop.close()
