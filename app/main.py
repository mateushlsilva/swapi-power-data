from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.lifespan import lifespan
from app.api.v1.endpoints.swRoutes import router as sw
from app.api.v1.endpoints.auth_routes import router as auth_router
from app.api.v1.endpoints.favorite_routes import router as favorite_router

app = FastAPI(title="SWAPI Power Data", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok"}

app.include_router(sw)
app.include_router(auth_router)
app.include_router(favorite_router)