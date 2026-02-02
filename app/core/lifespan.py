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
        os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"
        os.environ["GOOGLE_CLOUD_PROJECT"] = "demo-test"
        app.state.db = firestore.AsyncClient(project="demo-test")
        print("Firestore Emulator connected (localhost:8080)")
    else: 
        app.state.db = firestore.AsyncClient()
        print("Firestore Cloud connected")

    yield

    await redis_client.close()
    await app.state.db.close()
    print("Redis closed")
    print("Firestore closed")
