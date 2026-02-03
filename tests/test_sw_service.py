import pytest
import json
import httpx
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from app.services.starwars_service import StarWarsService

@pytest.mark.asyncio
async def test_get_resources_uses_cache():
    mock_redis = AsyncMock()
    mock_swapi = MagicMock()

    cached_payload = json.dumps({"results": [{"name": "Luke"}]})
    mock_redis.get.side_effect = [None, cached_payload] # status=None, cache=data

    service = StarWarsService(swapi_client=mock_swapi, redis=mock_redis)
    result = await service.get_resources("people")

    assert result["results"][0]["name"] == "Luke"
    mock_swapi.people.assert_not_called()

@pytest.mark.asyncio
async def test_circuit_breaker_blocks_when_open():
    mock_redis = AsyncMock()
    mock_swapi = MagicMock()
    mock_redis.get.return_value = "open"

    service = StarWarsService(swapi_client=mock_swapi, redis=mock_redis)

    with pytest.raises(HTTPException) as exc:
        await service.get_resources("people")
    
    assert exc.value.status_code == 503
    assert "Circuito aberto" in exc.value.detail

@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_failures():
    mock_redis = AsyncMock()
    mock_swapi = MagicMock()
    
    mock_redis.get.return_value = None # Circuito fechado e sem cache
    mock_redis.incr.return_value = 3 
    
    mock_swapi.people = AsyncMock(side_effect=httpx.RequestError("Timeout"))

    service = StarWarsService(swapi_client=mock_swapi, redis=mock_redis)

    with pytest.raises(HTTPException) as exc:
        await service.get_resources("people")

    assert exc.value.status_code == 504
    mock_redis.set.assert_any_call(service.status_key, "open", ex=service.recovery_time)

@pytest.mark.asyncio
async def test_update_nested_resources_resolution():
    mock_redis = AsyncMock()
    mock_swapi = MagicMock()
    
    mock_redis.get.return_value = None
    mock_swapi.get_url = AsyncMock(return_value={"title": "A New Hope"})

    service = StarWarsService(swapi_client=mock_swapi, redis=mock_redis)
    raw_data = {"films": ["https://swapi.dev/api/films/1/"]}
    
    result = await service._update_nested_resources(raw_data)

    assert result["films"] == ["A New Hope"]
    mock_redis.set.assert_called()