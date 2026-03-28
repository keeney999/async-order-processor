import pytest


@pytest.mark.asyncio
async def test_top_products_stats(client, db_session):

    response = await client.get("/api/v1/orders/stats/top-products")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_order_details(client, db_session):

    response = await client.get("/api/v1/orders/1/details")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == 1
    assert "items" in data
