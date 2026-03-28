from decimal import Decimal

import pytest
from sqlalchemy import select

from app.models.order import Order, OrderStatus
from app.models.outbox import Outbox
from app.models.product import Product
from app.models.user import User


@pytest.fixture
async def test_user(db_session):
    user = User(email="test@test.com", full_name="Test User", hashed_password="fake")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_products(db_session):
    products = [
        Product(name="Laptop", price=Decimal("999.99"), stock=10),
        Product(name="Mouse", price=Decimal("29.99"), stock=50),
        Product(name="Keyboard", price=Decimal("89.99"), stock=30),
    ]
    for p in products:
        db_session.add(p)
    await db_session.commit()
    for p in products:
        await db_session.refresh(p)
    return products


@pytest.mark.asyncio
async def test_create_order_success(client, db_session, test_user, test_products):
    payload = {
        "user_id": test_user.id,
        "items": [
            {"product_id": test_products[0].id, "quantity": 1},
            {"product_id": test_products[1].id, "quantity": 2},
        ],
    }
    response = await client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "order_id" in data

    order_id = data["order_id"]
    # Проверяем заказ
    result = await db_session.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one()
    assert order.status == OrderStatus.PENDING

    # Проверяем outbox
    result = await db_session.execute(
        select(Outbox).where(Outbox.event_type == "order_created")
    )
    outbox = result.scalar_one()
    assert outbox is not None


@pytest.mark.asyncio
async def test_create_order_insufficient_stock(
    client, db_session, test_user, test_products
):
    # Уменьшаем остаток
    test_products[0].stock = 1
    await db_session.commit()

    payload = {
        "user_id": test_user.id,
        "items": [
            {"product_id": test_products[0].id, "quantity": 2},
        ],
    }
    response = await client.post("/api/v1/orders/", json=payload)
    assert response.status_code == 400
    assert "Insufficient stock" in response.text
