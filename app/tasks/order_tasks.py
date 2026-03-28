"""Celery tasks for order processing."""

import asyncio
import logging
from decimal import Decimal

from sqlalchemy import text

from app.celery import celery_app
from app.core.database import async_session
from app.models.order import Order, OrderStatus

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_order(self, order_id: int) -> dict:
    """
    Process an order: reserve stock and update status.

    Uses atomic SQL update with stock check to prevent overselling.
    """
    logger.info(f"Processing order {order_id}")

    async def _process():
        async with async_session() as db:
            order = await db.get(Order, order_id)
            if not order:
                logger.error(f"Order {order_id} not found")
                return {"error": "Order not found"}

            if order.status != OrderStatus.PENDING:
                logger.info(
                    f"Order {order_id} already processed, status={order.status}"
                )
                return {"status": order.status.value}

            items = order.items
            if not items:
                logger.warning(f"Order {order_id} has no items")
                order.status = OrderStatus.FAILED
                await db.commit()
                return {"error": "No items"}

            product_ids = [item.product_id for item in items]
            quantities = [item.quantity for item in items]

            sql = text("""
                WITH updates AS (
                    SELECT id, stock, quantity
                    FROM unnest(:ids::int[], :quantities::int[]) AS t(id, quantity)
                    JOIN products p ON p.id = t.id
                    WHERE p.stock >= t.quantity
                )
                UPDATE products p
                SET stock = p.stock - u.quantity
                FROM updates u
                WHERE p.id = u.id
                RETURNING p.id
            """)
            result = await db.execute(
                sql, {"ids": product_ids, "quantities": quantities}
            )
            updated_ids = {row[0] for row in result.fetchall()}

            all_reserved = all(pid in updated_ids for pid in product_ids)

            if all_reserved:

                if order.total_amount is None:
                    total = Decimal("0")
                    for item in items:
                        total += item.price * item.quantity
                    order.total_amount = total

                order.status = OrderStatus.RESERVED
                await db.commit()
                logger.info(f"Order {order_id} reserved successfully")

                from app.tasks.payment_tasks import process_payment_task

                process_payment_task.delay(order_id)

                return {"status": "reserved", "order_id": order_id}
            else:
                failed_products = [pid for pid in product_ids if pid not in updated_ids]
                logger.warning(
                    f"Order {order_id} failed: insufficient stock for products {failed_products}"
                )
                order.status = OrderStatus.FAILED
                await db.commit()
                return {"error": "Insufficient stock"}

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_process())
    finally:
        loop.close()
