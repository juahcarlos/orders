import asyncio
import pytest

from httpx import AsyncClient
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from app.core import config
from app.main import app
from app.core.redis_init import rdb
from app.core.dependencies import get_current_user
from app.schemas.auth_schemas import UserContext
from app.schemas.order_schemas import OrderStatus
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.database import AsyncSessionLocal, Base, engine
from app.core.dependencies import get_db


conf = config.settings
TEST_DB_URL = f"postgresql+asyncpg://{conf.POSTGRES_USER}:{conf.POSTGRES_PASSWORD}@postgres:5432/test_db"

engine = create_async_engine(TEST_DB_URL)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

def pytest_configure(config):
    url = TEST_DB_URL.replace("+asyncpg", "")
    if not database_exists(url):
        create_database(url)

@pytest.fixture
async def db_session():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(autouse=True)
def override_db(db_session):
    app.dependency_overrides[get_db] = lambda: db_session

@pytest.fixture
async def auth_headers(ac):
    payload = {"email": "test@example.com", "password": "password"}
    payload_token = {"username": "test@example.com", "password": "password"}
    await ac.post("/auth/register", json=payload)
    res = await ac.post("/auth/token", data=payload_token)
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def ac():
    async with AsyncClient(app=app, base_url="http://app:8000/api") as client:
        yield client

@pytest.fixture(autouse=True)
def override_auth():
    app.dependency_overrides[get_current_user] = lambda: UserContext(user_id=1, email="t@t.com")
    yield
    # app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
async def override_rdb(test_rdb):
    app.dependency_overrides[rdb] = lambda: test_rdb
    yield
    # app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def test_rdb():
    client = Redis(host="redis", port=6379, db=1, decode_responses=True)
    yield client
    await client.flushdb()
    await client.close()

@pytest.fixture
async def clean_rdb(test_rdb):
    await test_rdb.flushdb()
    return test_rdb

@pytest.fixture
def order_payload():
    return {"items": "string", "total_price": 50.0}

@pytest.fixture
def patch_payload():
    return {"items": "new", "total_price": 100.0, "status": OrderStatus.PAID}