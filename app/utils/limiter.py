"""Rate limiting configuration using Slowapi and Redis."""
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address, 
    storage_uri=settings.storage_uri,
    default_limits=[settings.hour_max_limit, settings.minute_max_limit],
)