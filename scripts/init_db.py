import asyncio
import logging
from decimal import Decimal

from sqlmodel import select

from app.core.database import async_session
from app.core.logger import setup_logging
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User

setup_logging()
logger = logging.getLogger(__name__)


async def create_test_data():
    async with async_session() as db:
        # Проверяем, есть ли уже данные
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            logger.info("Test data already exists, skipping")
            return

        # Создаём пользователей
        users = [
            User(email="alice@example.com", full_name="Alice", hashed_password="fake"),
            User(email="bob@example.com", full_name="Bob", hashed_password="fake"),
        ]
        for u in users:
            db.add(u)
        await db.flush()

        # Создаём товары
        products = [
            Product(
                name="Laptop",
                description="High-performance laptop",
                price=Decimal("999.99"),
                stock=10,
            ),
            Product(
                name="Mouse",
                description="Wireless mouse",
                price=Decimal("29.99"),
                stock=50,
            ),
            Product(
                name="Keyboard",
                description="Mechanical keyboard",
                price=Decimal("89.99"),
                stock=30,
            ),
            Product(
                name="Monitor",
                description="4K monitor",
                price=Decimal("499.99"),
                stock=15,
            ),
            Product(
                name="Headphones",
                description="Noise cancelling",
                price=Decimal("199.99"),
                stock=25,
            ),
        ]
        for p in products:
            db.add(p)
        await db.flush()

        # Создаём несколько заказов для демонстрации статистики
        orders = [
            Order(
                user_id=users[0].id,
                status=OrderStatus.PAID,
                total_amount=Decimal("1029.98"),
            ),
            Order(
                user_id=users[1].id,
                status=OrderStatus.RESERVED,
                total_amount=Decimal("119.98"),
            ),
        ]
        for o in orders:
            db.add(o)
        await db.flush()

        order_items = [
            OrderItem(
                order_id=orders[0].id,
                product_id=products[0].id,
                quantity=1,
                price=products[0].price,
            ),
            OrderItem(
                order_id=orders[0].id,
                product_id=products[1].id,
                quantity=1,
                price=products[1].price,
            ),
            OrderItem(
                order_id=orders[1].id,
                product_id=products[2].id,
                quantity=1,
                price=products[2].price,
            ),
            OrderItem(
                order_id=orders[1].id,
                product_id=products[3].id,
                quantity=1,
                price=products[3].price,
            ),
        ]
        for oi in order_items:
            db.add(oi)
        await db.commit()

        logger.info(
            f"Created {len(users)} users, {len(products)} products, {len(orders)} orders"
        )


async def main():
    await create_test_data()
    logger.info("Database initialization complete.")


if __name__ == "__main__":
    asyncio.run(main())
