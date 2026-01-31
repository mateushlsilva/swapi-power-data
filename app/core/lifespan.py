from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = Redis.from_url(settings.REDIS, decode_responses=True)
    app.state.redis = redis_client
    print("Redis connection")
    yield

    await redis_client.close()
    print("Redis closed")
