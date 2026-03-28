"""Order API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
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


@router.get("/stats/top-products")
async def top_products_by_revenue(db: AsyncSession = Depends(get_session)):
    """
    Get top 5 products by revenue in the last 30 days using a window function.
    """
    query = text("""
        WITH revenue AS (
            SELECT
                p.id,
                p.name,
                SUM(oi.quantity * oi.price) as product_revenue,
                RANK() OVER (ORDER BY SUM(oi.quantity * oi.price) DESC) as rank
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            JOIN orders o ON oi.order_id = o.id
            WHERE o.created_at >= now() - interval '30 days'
            GROUP BY p.id
        )
        SELECT id, name, product_revenue, rank
        FROM revenue
        WHERE rank <= 5
        ORDER BY rank
    """)
    result = await db.execute(query)
    rows = result.mappings().all()
    return [dict(row) for row in rows]


@router.get("/{order_id}/details")
async def get_order_details(order_id: int, db: AsyncSession = Depends(get_session)):
    """
    Get order details with calculated total using a window function.
    """
    query = text("""
        SELECT
            o.id,
            o.user_id,
            o.status,
            o.total_amount,
            o.created_at,
            oi.product_id,
            oi.quantity,
            oi.price,
            SUM(oi.quantity * oi.price) OVER (PARTITION BY o.id) as calculated_total
        FROM orders o
        LEFT JOIN order_items oi ON o.id = oi.order_id
        WHERE o.id = :order_id
    """)
    result = await db.execute(query, {"order_id": order_id})
    rows = result.mappings().all()
    return {"order_id": order_id, "items": rows}
