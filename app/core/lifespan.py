from contextlib import asynccontextmanager
from fastapi import FastAPI
from redis.asyncio import Redis
from google.cloud import firestore
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_client = Redis.from_url(settings.REDIS, decode_responses=True)
    app.state.redis = redis_client
    print("Redis connection")

    if settings.ENVIRONMENT != "prod":
        import os
        app.state.db = firestore.AsyncClient(project="demo-test")
        
        emu_host = os.getenv("FIRESTORE_EMULATOR_HOST")
        print(f"Firestore Emulator connected to: {emu_host}")
    else: 
        app.state.db = firestore.AsyncClient()
        print("Firestore Cloud connected")

    yield

    await redis_client.close()
    await app.state.db.close()
    print("Redis closed")
    print("Firestore closed")
