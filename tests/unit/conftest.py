import fakeredis.aioredis
import pytest
import uuid

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from app.models.models import Order, User
from app.repositories.user import UserRepository
from app.schemas.auth_schemas import LoginRequest, UserContext
from app.schemas.order_schemas import OrderCreate, OrderResponse, OrderStatus
from app.services.auth_service import AuthService
from app.services.jwt_services import JWTService
from app.services.order_service import OrderService



@pytest.fixture
def order_repo():
    return AsyncMock()

@pytest.fixture
def order_service(order_repo, fake_rdb):
    return OrderService(order_repo)

@pytest.fixture
def order_create_data():
    return OrderCreate(
        items="item1,item2",
        total_price=100,
        status=OrderStatus.PENDING,
    )

@pytest.fixture
def order_update_data(order_create_data):
    return OrderCreate(
        items="item1,item2",
        total_price=100,
        status=OrderStatus.PAID,
    )


@pytest.fixture
def order_model(order_id):
    order = OrderResponse(
        id=order_id,
        user_id=1,
        items="item1,item2",
        total_price=Decimal("100.00"),
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
    )
    return order 


@pytest.fixture
def order_model_patch(order_model):
    order = order_model
    order.status=OrderStatus.PAID
    return order
 

@pytest.fixture
def order_id():
    return uuid.uuid4()

@pytest.fixture
def user_id():
    return 1

@pytest.fixture
def mock_order(order_model, order_id):
    order_model.id = order_id
    return order_model

@pytest.fixture
def mock_order_user(order_model):
    return [order_model]

# cache

@pytest.fixture
async def fake_rdb(mocker):
    client = fakeredis.aioredis.FakeRedis(decode_responses=True)
    mocker.patch("app.services.order_service.rdb", client)
    return client

# auth

@pytest.fixture
def jwt_service():
    return JWTService()

@pytest.fixture
def mock_user_repo_none():
    repo = AsyncMock(spec=UserRepository)
    repo.get_by_email.return_value = None
    return repo

@pytest.fixture
def mock_user_repo_wrong_password(jwt_service):
    repo = AsyncMock(spec=UserRepository)
    user = AsyncMock()
    user.hashed_password = jwt_service.hash_password("correctpass")
    repo.get_by_email.return_value = user
    return repo

@pytest.fixture
def mock_user_repo_success(jwt_service):
    repo = AsyncMock(spec=UserRepository)
    user = AsyncMock()
    user.id = 1
    user.email = "user@test.com"
    user.hashed_password = jwt_service.hash_password("pass123")
    repo.get_by_email.return_value = user
    return repo

@pytest.fixture
def auth_service_user_not_found(mock_user_repo_none, jwt_service):
    service = AuthService(jwt_service)
    service.user_repo = mock_user_repo_none
    return service

@pytest.fixture
def auth_service_wrong_password(mock_user_repo_wrong_password, jwt_service):
    service = AuthService(jwt_service)
    service.user_repo = mock_user_repo_wrong_password
    return service

@pytest.fixture
def auth_service_success(mock_user_repo_success, jwt_service):
    service = AuthService(jwt_service)
    service.user_repo = mock_user_repo_success
    return service


@pytest.fixture
def test_app(mock_user_repo_none):
    from app.main import app # импорт твоих зависимостей
    from app.core.dependencies import get_user_repository 
    app.dependency_overrides[get_user_repository] = lambda: mock_user_repo_none
    yield app
    app.dependency_overrides.clear()


@pytest.fixture
def login_request():
    return LoginRequest(email="user@test.com", password="pass123")
