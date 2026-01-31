from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.lifespan import lifespan
from app.api.v1.endpoints.swRoutes import router as sw

app = FastAPI(title="SWAPI Power Data", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sw)