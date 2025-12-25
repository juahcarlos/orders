"""
Orders Service entry point.
Configures FastAPI app, CORS, Rate Limiting, and API routing.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.auth import router as auth_router
from app.api.orders import router as orders_router
from app.core.config import settings
from app.kafka.kafka_client import KafkaManager
from app.utils.logs import log
from app.core.redis_init import rdb
from app.utils.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage infrastructure connections.
    Establish rdb and Kafka sessions on startup; close sessions on shutdown.
    """
    await rdb.ping()
    await KafkaManager.start()
    log.debug("Services started")
    
    yield
    
    await KafkaManager.stop()
    await rdb.close()
    log.debug("Services stopped")


app = FastAPI(
    title="Orders",
    description="Orders receiving service with auth",
    version="0.1.0",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(orders_router, prefix=settings.api_prefix)

