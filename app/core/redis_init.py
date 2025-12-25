from redis import asyncio as aioredis

rdb = aioredis.Redis.from_url("redis://redis:6379/0", decode_responses=True)