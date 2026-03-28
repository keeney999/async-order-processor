"""RabbitMQ connection and publishing utilities."""

import logging
from typing import Optional

import aio_pika
from aio_pika import ExchangeType, Message

from app.core.config import settings

logger = logging.getLogger(__name__)

_connection: Optional[aio_pika.Connection] = None
_channel: Optional[aio_pika.Channel] = None


async def get_connection() -> aio_pika.Connection:
    """Get or create a persistent RabbitMQ connection."""
    global _connection
    if _connection is None or _connection.is_closed:
        _connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    return _connection


async def get_channel() -> aio_pika.Channel:
    """Get or create a channel on the persistent connection."""
    global _channel
    conn = await get_connection()
    if _channel is None or _channel.is_closed:
        _channel = await conn.channel()
        await _channel.declare_exchange(
            "orders",
            ExchangeType.TOPIC,
            durable=True,
        )
        logger.debug("Exchange 'orders' declared")
    return _channel


async def publish_message(
    exchange: str,
    routing_key: str,
    message: str,
) -> None:
    """
    Publish a message to a RabbitMQ exchange.

    Args:
        exchange: Exchange name.
        routing_key: Routing key for the message.
        message: String payload.
    """
    channel = await get_channel()
    exch = await channel.get_exchange(exchange, ensure=True)
    msg = Message(
        body=message.encode(),
        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
    )
    await exch.publish(msg, routing_key=routing_key)
    logger.debug(f"Published to {exchange}/{routing_key}: {message[:100]}")


async def close_connection() -> None:
    """Close RabbitMQ connection gracefully."""
    global _connection, _channel
    if _channel and not _channel.is_closed:
        await _channel.close()
    if _connection and not _connection.is_closed:
        await _connection.close()
    _channel = None
    _connection = None
