import asyncio
import logging
import sys
from decimal import Decimal

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, select

from app.core.config import settings
from app.core.database import async_session
from app.core.logger import setup_logging
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User

setup_logging()
logger = logging.getLogger(__name__)


async def recreate_tables():
    """Drop all tables and recreate them."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Tables recreated.")
    await engine.dispose()


async def create_tables_if_not_exist():
    """Create tables if they don't exist."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        result = await conn.execute(
            text(
                "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user')"
            )
        )
        exists = result.scalar()
        if not exists:
            await conn.run_sync(SQLModel.metadata.create_all)
            logger.info("Tables created.")
    await engine.dispose()


async def create_test_data():
    async with async_session() as db:
        result = await db.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            logger.info("Test data already exists, skipping")
            return

        users = [
            User(email="alice@example.com", full_name="Alice", hashed_password="fake"),
            User(email="bob@example.com", full_name="Bob", hashed_password="fake"),
        ]
        for u in users:
            db.add(u)
        await db.flush()

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
    if "--force" in sys.argv:
        await recreate_tables()
    else:
        await create_tables_if_not_exist()
    await create_test_data()


if __name__ == "__main__":
    asyncio.run(main())
