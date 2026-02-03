from fastapi import Request
from app.services.auth_service import AuthService
from app.repository.firestore_repository import FirestoreRepository
from app.services.starwars_service import StarWarsService
from app.utils import jwt, auth, validated
from app.integration.SwapiClient import SwapiClient

async def get_redis(request: Request):
    return request.app.state.redis

async def get_db(request: Request):
    return request.app.state.db

async def get_auth_service(request: Request) -> AuthService:
    db = request.app.state.db
    
    repository = FirestoreRepository(db)
    
    jwt_tool = jwt.Jwt()
    auth_tool = auth.Auth()
    validators = validated.Validadores()
    
    return AuthService(
        repository=repository, 
        jwt=jwt_tool, 
        auth=auth_tool,
        validated=validators
    )


async def get_firestore_repository(request: Request) -> FirestoreRepository:
    db = request.app.state.db
    return FirestoreRepository(db)

async def get_swapi_service(request: Request) -> StarWarsService:
    redis = request.app.state.redis
    swapi_client = SwapiClient()
    return StarWarsService(swapi_client, redis)