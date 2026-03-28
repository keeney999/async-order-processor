"""Celery periodic task for outbox processing."""

import asyncio
import logging

from app.celery import celery_app
from app.services.outbox_service import publish_pending_events

logger = logging.getLogger(__name__)


@celery_app.task
def publish_outbox() -> None:
    """Publish all pending outbox events."""
    logger.info("Processing outbox")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(publish_pending_events())
    finally:
        loop.close()
