import pytest
from httpx import AsyncClient
from app.main import app
from app.models.models import Order


@pytest.mark.asyncio
async def test_order_process(clean_rdb, auth_headers, ac):
        payload = {"items": "item1", "total_price": 100.0, "user_id": 1}
        # Create
        resp = await ac.post("/orders/", json=payload, headers=auth_headers)
        assert resp.status_code == 201
        oid = resp.json()["id"]
        # Read
        resp = await ac.get(f"/orders/{oid}/", headers=auth_headers)
        assert resp.status_code == 200

@pytest.mark.asyncio
async def test_patch_order_db_and_cache(ac, db_session, auth_headers, test_rdb, order_payload, patch_payload):
    # Create
    res = await ac.post("/orders/", json=order_payload, headers=auth_headers)
    order_id = res.json()["id"]

    # Patch
    resp = await ac.patch(f"/orders/{order_id}", json=patch_payload, headers=auth_headers)
    assert resp.status_code == 200

    # DB & Cache
    order_db = await db_session.get(Order, order_id)
    assert order_db.status == "PAID"
    assert await test_rdb.get(f"order:{order_id}") is None

@pytest.mark.asyncio
async def test_get_order_db_and_cache(ac, db_session, auth_headers, test_rdb, order_payload):
    # Create order
    c_res = await ac.post("/orders/", json=order_payload, headers=auth_headers)
    order_id = c_res.json()["id"]

    # GET
    resp = await ac.get(f"/orders/{order_id}/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["items"] == order_payload["items"]

@pytest.mark.asyncio
async def test_get_order_user_db_and_cache(ac, db_session, auth_headers, test_rdb, order_payload):
    # Create order
    c_res = await ac.post("/orders/", json=order_payload, headers=auth_headers)
    order_id = c_res.json()["id"]

    # GET
    user_id = 1
    resp = await ac.get(f"/orders/user/{user_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()[0]["items"] == order_payload["items"]

