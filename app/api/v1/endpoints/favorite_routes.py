from typing import Optional
from fastapi import APIRouter, Depends, Response, Query, Body, status

from app.core.deps import get_firestore_repository, get_swapi_service
from app.middleware.authorization import Authorization
from app.repository.firestore_repository import FirestoreRepository
from app.schemas.favorites.sw_favorites import SWFavoriteCreate, SWFavoriteRequestCreate, SWFavoriteRead, SWFavorite
from app.schemas.sw.sw_resouce import SWResource
from app.services.favorite_service import FavoriteService
from app.services.starwars_service import StarWarsService


router = APIRouter(
    prefix="/favorite",
    tags=["Favorite"],
    responses={
        200: {"description": "Sucesso: Dados recuperados."},
        400: {"description": "Erro na requisição: Parâmetros inválidos ou malformados."},
        401: {"description": "Not authenticated"},
        403: {"description": "Acesso negado"},
        404: {"description": "Não encontrado: O recurso solicitado não existe na base."},
        500: {"description": "Erro interno: Falha inesperada no processamento do servidor."},
        503: {"description": "Serviço Indisponível: Circuito aberto. As chamadas foram bloqueadas temporariamente."},
        504: {"description": "Gateway Timeout: A SWAPI demorou demais para responder (mesmo após retentativas)."}
    },
    dependencies=[Depends(Authorization(["common", 'admin']))]
)

@router.get(
    "/{favorite_id}",
    summary="Obter Favorito",
    description="Retorna um favorito específico pelo ID.",
    response_description="Favorito retornado com sucesso.",
    response_model=SWFavoriteRead
)
async def get_favorite(
    favorite_id: str,
    repository: FirestoreRepository = Depends(get_firestore_repository),
    sw_service: StarWarsService = Depends(get_swapi_service),
    user: str = Depends(Authorization(["common", 'admin']))
):
    service = FavoriteService(repository, sw_service)
    return await service.get_favorite_id(user['sub'], favorite_id)


@router.get(
    "/",
    summary="Listar Favoritos",
    description="Lista os favoritos do usuário autenticado, com suporte a filtros e paginação.",
    response_description="Lista de favoritos retornada com sucesso.",
    response_model=list[SWFavorite]
)
async def list_favorites(
    repository: FirestoreRepository = Depends(get_firestore_repository),
    sw_service: StarWarsService = Depends(get_swapi_service),
    user: str = Depends(Authorization(["common", 'admin'])),
    resource: Optional[SWResource] = Query(None, description="Filtra por tipo de recurso (ex: people, films)"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de favoritos a serem retornados."),
    last_id: Optional[str] = Query(None, description="ID do último favorito da página anterior para paginação.")
):
    service = FavoriteService(repository, sw_service)
    filters = []
    if resource:
        filters.append(("resource", "==", resource.value))
    return await service.list_favorites(user['sub'], filters=filters, limit=limit, last_id=last_id)

@router.post(
    "/",
    summary="Adicionar Favorito",
    description="Adiciona um recurso aos favoritos.",
    response_description="Recurso adicionado aos favoritos com sucesso.",
    status_code=status.HTTP_201_CREATED
)
async def add_favorite(
    favorite_create: SWFavoriteRequestCreate = Body(..., description="Dados do recurso a ser adicionado aos favoritos."),
    repository: FirestoreRepository = Depends(get_firestore_repository),
    user: str = Depends(Authorization(["common", 'admin']))
):
    service = FavoriteService(repository)
    favorite_create_data: SWFavoriteCreate = SWFavoriteCreate(**favorite_create.model_dump(), user_id=user['sub'])
    return await service.add_favorite(favorite_create_data)


@router.delete(
    "/{favorite_id}",
    summary="Remover Favorito",
    description="Remove um recurso dos favoritos pelo ID.",
    response_description="Recurso removido dos favoritos com sucesso.",
    responses={
        204: {"description": "Favorito removido com sucesso."}
    },
    status_code=status.HTTP_204_NO_CONTENT
)
async def remove_favorite(
    favorite_id: str,
    repository: FirestoreRepository = Depends(get_firestore_repository),
    user: str = Depends(Authorization(["common", 'admin']))
):
    service = FavoriteService(repository)
    return await service.remove_favorite(favorite_id, user['sub'])
    