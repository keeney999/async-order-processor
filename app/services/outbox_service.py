"""Outbox service for publishing events."""

from app.core.logger import get_logger

logger = get_logger(__name__)


def publish_pending_events() -> None:
    """Fetch pending outbox events and publish them to RabbitMQ."""
    logger.info("Publishing pending events")
