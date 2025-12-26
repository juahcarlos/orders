import json
from unittest.mock import patch

import pytest
from fastapi import HTTPException

from app.schemas.auth_schemas import LoginRequest
from app.schemas.order_schemas import OrderStatus


@pytest.mark.asyncio
async def test_create_order(order_service, order_repo, order_create_data, order_model):
    order_repo.create_order.return_value = order_model

    result = await order_service.create_order(
        data=order_create_data,
        user_id=1,
    )

    order_repo.create_order.assert_awaited_once()
    assert result.user_id == 1
    assert result.items == order_create_data.items
    assert result.status == OrderStatus.PENDING


@pytest.mark.asyncio
async def test_patch_order(order_service, order_repo, order_update_data, order_model_patch, order_id):
    order_repo.update_order.return_value = order_model_patch

    result = await order_service.patch_order(
        data=order_update_data,
        order_id=order_id,
    )

    order_repo.update_order.assert_awaited_once()
    assert result.user_id == order_model_patch.user_id
    assert result.items == order_model_patch.items
    assert result.status == OrderStatus.PAID


@pytest.mark.asyncio
async def test_get_order_success(order_service, order_repo, order_model, order_id):
    order_repo.get_order.return_value = order_model
    result = await order_service.get_order(order_id)
    assert result.id == order_id


@pytest.mark.asyncio
async def test_get_order_not_found(order_service, order_repo, order_id):
    order_repo.get_order.return_value = None

    with pytest.raises(HTTPException) as exc:
        await order_service.get_order(order_id=order_id)

    assert exc.value.status_code == 404
    assert "Order not found" in exc.value.detail


@pytest.mark.asyncio
async def test_get_order_user_success(order_service, order_repo, mock_order_user, user_id):
    order_repo.get_order_user.return_value = mock_order_user
    result = await order_service.get_order_user(user_id)
    assert result[0].user_id == user_id


@pytest.mark.asyncio
async def test_get_order_user_not_found(order_service, order_repo, user_id):
    order_repo.get_order.return_value = None

    with pytest.raises(HTTPException) as exc:
        await order_service.get_order_user(user_id=user_id)

    assert exc.value.status_code == 404
    assert f"No orders for user {user_id}" in exc.value.detail

# cache

@pytest.mark.asyncio
async def test_service_get_order_cache_hit(order_service, fake_rdb, order_repo, order_model, order_id):
    """Ensures that if data exists in Redis, the service returns it
    immediately without calling the repository."""
    await fake_rdb.set(f"order:{order_id}", order_model.model_dump_json())

    order_repo.get_order.return_value = order_model

    result = await order_service.get_order(order_id)
    assert result.id == order_id


@pytest.mark.asyncio
async def test_service_get_order_cache_miss(order_service, fake_rdb, order_repo, order_model, order_id):
    """Verifies that when data is missing in Redis,
    the service fetches it from the repository and populates the cache."""
    await fake_rdb.flushall()
    order_repo.get_order.return_value = order_model

    result = await order_service.get_order(order_id)

    assert result.id == order_id
    order_repo.get_order.assert_awaited_once_with(id=order_id)
    assert await fake_rdb.exists(f"order:{order_id}")


@pytest.mark.asyncio
async def test_service_patch_updates_cache(order_service, fake_rdb, order_repo, order_model_patch, order_update_data, order_id):
    """Confirms that updating an order via the service
    also refreshes the corresponding record in the cache."""
    order_repo.update_order.return_value = order_model_patch

    await order_service.patch_order(order_id, order_update_data)

    cached = await fake_rdb.get(f"order:{order_id}")
    assert json.loads(cached)["status"] == OrderStatus.PAID


# auth

@pytest.mark.asyncio
async def test_auth_success(auth_service_success, login_request):
    tokens = await auth_service_success.token(login_request, db=None)
    assert "access_token" in tokens
    assert "refresh_token" in tokens


@pytest.mark.asyncio
async def test_auth_success(auth_service_success, mock_user_repo_success):
    request = LoginRequest(email="user@test.com", password="pass123")

    with patch("app.services.auth_service.UserRepository") as mocked_class:
        mocked_class.return_value = mock_user_repo_success
        tokens = await auth_service_success.token(request, db=None)

    assert tokens['access_token'] is not None


@pytest.mark.asyncio
async def test_auth_wrong_password(auth_service_wrong_password, mock_user_repo_wrong_password):
    request = LoginRequest(email="user@test.com", password="wrongpass")

    with patch("app.services.auth_service.UserRepository") as mocked_class:
        mocked_class.return_value = mock_user_repo_wrong_password

        with pytest.raises(HTTPException) as exc:
            await auth_service_wrong_password.token(request, db=None)

    assert exc.value.status_code == 401
    assert "Incorrect email or password" in exc.value.detail
