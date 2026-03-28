import pytest

from app.models.outbox import Outbox, OutboxStatus
from app.services.outbox_service import publish_pending_events


@pytest.mark.asyncio
async def test_outbox_publish(db_session):
    outbox = Outbox(event_type="test_event", payload='{"key":"value"}')
    db_session.add(outbox)
    await db_session.commit()

    await publish_pending_events()

    await db_session.refresh(outbox)
    assert outbox.status == OutboxStatus.SENT
