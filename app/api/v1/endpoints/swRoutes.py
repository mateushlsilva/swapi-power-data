from fastapi import APIRouter, Depends, Response, Query, Body, status
from typing import List, Optional
from fastapi.responses import JSONResponse
from app.core.deps import get_redis
from app.services.starwars_service import StarWarsService
from app.integration.SwapiClient import SwapiClient
from app.schemas.sw_resouce import SWResource  
from app.schemas.sw import SWPeopleRead, SWFilmsRead, SWPlanetsRead, SWSpeciesRead, SWStarshipsRead, SWVehiclesRead, SWAnyDetailsRead

router = APIRouter(
    prefix="/sw",
    tags=["Star Wars"],
    responses={
        200: {"description": "Sucesso: Dados recuperados da SWAPI ou do Cache."},
        400: {"description": "Erro na requisição: Parâmetros inválidos ou malformados."},
        404: {"description": "Não encontrado: O recurso solicitado não existe na base da SWAPI."},
        500: {"description": "Erro interno: Falha inesperada no processamento do servidor."},
        503: {"description": "Serviço Indisponível: Circuito aberto. A SWAPI está instável e as chamadas foram bloqueadas temporariamente."},
        504: {"description": "Gateway Timeout: A SWAPI demorou demais para responder (mesmo após retentativas)."}
    }
)

swapi_client = SwapiClient()

@router.get(
    "/people",
    summary="Listar Personagens",
    description=(
        "Busca personagens da franquia Star Wars. "
        "Possui suporte a **busca por nome**, **paginação** e conta com uma camada de **Cache no Redis** "
        "e um sistema de **Circuit Breaker** para garantir a resiliência caso a SWAPI esteja instável."
    ),
    response_description="Lista de personagens encontrada com sucesso.",
    response_model=SWPeopleRead
)
async def get_people(
    name: Optional[str] = Query(None, alias="search", description="Nome do personagem para pesquisa (ex: Luke)"),
    page: Optional[int] = Query(None, ge=1, description="Número da página para paginação"),
    redis=Depends(get_redis)
):
    service = StarWarsService(swapi_client, redis)
    return await service.get_resources("people", name=name, page=page)



@router.get(
    "/films",
    summary="Listar Filmes",
    description="Busca filmes da franquia Star Wars com suporte a cache e resiliência.",
    response_description="Lista de filmes encontrada com sucesso.",
    response_model=SWFilmsRead
)
async def get_films(
    name: Optional[str] = Query(None, alias="search", description="Título do filme para pesquisa"),
    page: Optional[int] = Query(None, ge=1, description="Número da página para paginação"),
    redis=Depends(get_redis)
):
    service = StarWarsService(swapi_client, redis)
    return await service.get_resources("films", name=name, page=page)

@router.get(
    "/planets",
    summary="Listar Planetas",
    description="Busca planetas da franquia Star Wars com suporte a cache e resiliência.",
    response_description="Lista de planetas encontrada com sucesso.",
    response_model=SWPlanetsRead
)
async def get_planets(
    name: Optional[str] = Query(None, alias="search", description="Nome do planeta para pesquisa"),
    page: Optional[int] = Query(None, ge=1, description="Número da página para paginação"),
    redis=Depends(get_redis)
):
    service = StarWarsService(swapi_client, redis)
    return await service.get_resources("planets", name=name, page=page)


@router.get(
    "/species",
    summary="Listar Espécies",
    description="Busca espécies da franquia Star Wars com suporte a cache e resiliência.",
    response_description="Lista de espécies encontrada com sucesso.",
    response_model=SWSpeciesRead
)
async def get_species(
    name: Optional[str] = Query(None, alias="search", description="Nome da espécie para pesquisa"),
    page: Optional[int] = Query(None, ge=1, description="Número da página para paginação"),
    redis=Depends(get_redis)
):
    service = StarWarsService(swapi_client, redis)
    return await service.get_resources("species", name=name, page=page)


@router.get(
    "/starships",
    summary="Listar Naves",
    description="Busca naves espaciais da franquia Star Wars com suporte a cache e resiliência.",
    response_description="Lista de naves encontrada com sucesso.",
    response_model=SWStarshipsRead
)
async def get_starships(
    name: Optional[str] = Query(None, alias="search", description="Nome da nave para pesquisa"),
    page: Optional[int] = Query(None, ge=1, description="Número da página para paginação"),
    redis=Depends(get_redis)
):
    service = StarWarsService(swapi_client, redis)
    return await service.get_resources("starships", name=name, page=page)


@router.get(
    "/vehicles",
    summary="Listar Veículos",
    description="Busca veículos da franquia Star Wars com suporte a cache e resiliência.",
    response_description="Lista de veículos encontrada com sucesso.",
    response_model=SWVehiclesRead
)
async def get_vehicles(
    name: Optional[str] = Query(None, alias="search", description="Nome do veículo para pesquisa"),
    page: Optional[int] = Query(None, ge=1, description="Número da página para paginação"),
    redis=Depends(get_redis)
):
    service = StarWarsService(swapi_client, redis)
    return await service.get_resources("vehicles", name=name, page=page)

@router.get(
    "/details/{resource}/{id}",
    summary="Obter Detalhes Enriquecidos",
    description="Busca informações detalhadas de um recurso específico da SWAPI (Personagens, Filmes, Planetas, etc.)",
    response_description="Objeto detalhado com todos os campos de relacionamento convertidos em nomes amigáveis.",
    response_model=SWAnyDetailsRead
)
async def get_details(
    resource: SWResource,
    id: str,
    redis=Depends(get_redis)
):
    service = StarWarsService(swapi_client, redis)
    return await service.get_details(resource, id)