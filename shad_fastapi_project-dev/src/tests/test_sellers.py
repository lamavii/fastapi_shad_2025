import pytest
from fastapi import status
from jose import jwt
from sqlalchemy import select

from src.models import sellers
from src.routers.v1.token import SECRET_KEY, ALGORITHM


@pytest.mark.asyncio
async def test_create_seller(async_client):
    data = {"first_name": "Seller", "last_name": "Sellerow", "email": "seller1@mail.ru", "password": "password1"}
    response = await async_client.post("/api/v1/seller/", json=data)
    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()

    assert result_data == {
        "id": 2,
        "first_name": "Seller",
        "last_name": "Sellerow",
        "email": "seller1@mail.ru"
    }


@pytest.mark.asyncio
async def test_get_sellers(db_session, async_client):
    seller = sellers.Seller(first_name="Seller", last_name="Sellerow", email="seller2@mail.ru", password="password1")
    seller_2 = sellers.Seller(first_name="Seller", last_name="Sellerow", email="seller3@mail.ru", password="password1")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/seller/")

    assert response.status_code == status.HTTP_200_OK

    response_data = response.json()["sellers"]
    response_sellers_emails = {seller["email"] for seller in response_data}

    assert "seller2@mail.ru" in response_sellers_emails
    assert "seller3@mail.ru" in response_sellers_emails


@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Seller", last_name="Sellerow", email="seller4@mail.ru", password="password1")

    token_data = {"sub": seller.email}
    test_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    db_session.add_all([seller])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/seller/{seller.id}", headers={"Authorization": f"Bearer {test_token}"})

    assert response.status_code == status.HTTP_200_OK

    assert response.json() == {
        "first_name": "Seller",
        "last_name": "Sellerow",
        "email": "seller4@mail.ru",
        "id": seller.id,
        "books": []
    }


@pytest.mark.asyncio
async def test_delete_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Seller", last_name="Sellerow", email="seller5@mail.ru", password="password1")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/seller/{seller.id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()

    response_sellers_emails = {seller.email for seller in res}

    assert "seller5@mail.ru" not in response_sellers_emails


@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):
    seller = sellers.Seller(first_name="Seller", last_name="Sellerow", email="seller6@mail.ru", password="password1")

    db_session.add(seller)
    await db_session.flush()

    response = await async_client.put(
        f"/api/v1/seller/{seller.id}",
        json={"first_name": "AnotherSeller", "last_name": "AnotherSellerow", "email": "anotherseller6@mail.ru"},
    )
    print(response.json)
    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    res = await db_session.get(sellers.Seller, seller.id)
    assert res.first_name == "AnotherSeller"
    assert res.last_name == "AnotherSellerow"
    assert res.email == "anotherseller6@mail.ru"
