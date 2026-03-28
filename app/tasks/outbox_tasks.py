"""Outbox processing tasks."""

from app.celery import celery_app
from app.core.logger import get_logger
from app.services.outbox_service import publish_pending_events

logger = get_logger(__name__)


@celery_app.task
def publish_outbox() -> None:
    """Publish all pending outbox events."""
    logger.info("Processing outbox")
    publish_pending_events()
