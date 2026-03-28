from decimal import Decimal

import pytest

from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.tasks.order_tasks import process_order


@pytest.mark.asyncio
async def test_process_order_success(db_session):
    # Setup
    user = User(email="test@test.com", full_name="Test User", hashed_password="fake")
    db_session.add(user)
    product = Product(name="Test", price=Decimal("10.00"), stock=5)
    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(user)
    await db_session.refresh(product)

    order = Order(user_id=user.id, status=OrderStatus.PENDING)
    db_session.add(order)
    await db_session.flush()
    order_item = OrderItem(
        order_id=order.id, product_id=product.id, quantity=2, price=product.price
    )
    db_session.add(order_item)
    await db_session.commit()
    await db_session.refresh(order)

    # Call task (synchronous call, it runs in current process)
    result = process_order(order.id)
    assert result["status"] == "reserved"

    # Check database
    await db_session.refresh(order)
    assert order.status == OrderStatus.RESERVED
    await db_session.refresh(product)
    assert product.stock == 3
