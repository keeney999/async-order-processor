"""Outbox service for publishing events to RabbitMQ."""

import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import async_session
from app.models.outbox import Outbox, OutboxStatus
from app.utils.rabbit import publish_message

logger = logging.getLogger(__name__)


async def publish_pending_events() -> None:
    """Fetch pending outbox events and publish them to RabbitMQ."""
    async with async_session() as db:
        result = await db.execute(
            select(Outbox)
            .where(Outbox.status == OutboxStatus.PENDING)
            .order_by(Outbox.created_at)
            .limit(100)
        )
        events = result.scalars().all()

        for event in events:
            success = await _publish_event(db, event)
            if not success:
                logger.error(f"Failed to publish event {event.id}, will retry later")


async def _publish_event(db: AsyncSession, event: Outbox) -> bool:
    """
    Publish a single outbox event to RabbitMQ.

    Args:
        db: Database session.
        event: Outbox record.

    Returns:
        True if published successfully, False otherwise.
    """
    try:
        await publish_message(
            exchange="orders",
            routing_key=event.event_type,
            message=event.payload,
        )
        await db.execute(
            update(Outbox)
            .where(Outbox.id == event.id)
            .values(status=OutboxStatus.SENT, processed_at=event.created_at)
        )
        await db.commit()
        logger.info(f"Published outbox event {event.id} ({event.event_type})")
        return True
    except Exception as e:
        logger.exception(f"Error publishing event {event.id}: {e}")
        await db.execute(
            update(Outbox)
            .where(Outbox.id == event.id)
            .values(
                status=OutboxStatus.FAILED,
                retries=event.retries + 1,
                last_error=str(e),
            )
        )
        await db.commit()
        return False
