"""Celery tasks for order processing."""

from app.celery import celery_app
from app.core.logger import get_logger

logger = get_logger(__name__)


@celery_app.task(bind=True, max_retries=3)
def process_order(self, order_id: int) -> dict:
    """Process an order: reserve stock, calculate final amount."""
    logger.info(f"Processing order {order_id}")
    return {"order_id": order_id, "status": "processed"}
