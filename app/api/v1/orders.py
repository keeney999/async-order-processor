"""Order API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.order import OrderCreate
from app.services.order_service import create_order_with_outbox

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def create_order(
    order_data: OrderCreate,
    db: AsyncSession = Depends(get_session),
) -> dict:
    """
    Create a new order and publish event to outbox.

    The order will be processed asynchronously by a worker.
    """
    try:
        order_id = await create_order_with_outbox(db, order_data)
        return {"order_id": order_id, "message": "Order accepted for processing"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
