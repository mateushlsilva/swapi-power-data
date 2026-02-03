import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.favorite_service import FavoriteService
from app.schemas.favorites.sw_favorites import SWFavoriteCreate
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_remove_favorite_wrong_user_raises_404():
    mock_repository = MagicMock()
    mock_repository.find_by_id = AsyncMock(return_value={
        "id": "fav_1",
        "user_id": "user_2_abc"
    })

    service = FavoriteService(repository=mock_repository, sw_service=None)

    with pytest.raises(HTTPException) as exc_info:
        await service.remove_favorite(favorite_id="fav_1", user_id="user_1_abc")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Favorito não encontrado."


@pytest.mark.asyncio
async def test_remove_favorite_success():
    mock_repository = MagicMock()
    mock_repository.find_by_id = AsyncMock(return_value={
        "id": "fav_1",
        "user_id": "user_1_abc"
    })

    mock_repository.delete = AsyncMock(return_value=True)

    service = FavoriteService(repository=mock_repository, sw_service=None)

    result = await service.remove_favorite(favorite_id="fav_1", user_id="user_1_abc")
    assert result is True
    mock_repository.delete.assert_called_once()


@pytest.mark.asyncio
async def test_add_favorite_invalid_url_raises_400():
    mock_repository = MagicMock()
    service = FavoriteService(repository=mock_repository, sw_service=None)

    invalid_favorite = SWFavoriteCreate(
        user_id="user_1_abc",
        sw_id="1",
        resource="people",
        url="people/1",
        name="Luke Skywalker"
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.add_favorite(invalid_favorite)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "URL inválida. Deve começar com 'https://'"


@pytest.mark.asyncio
async def test_add_favorite_non_integer_sw_id_raises_400():
    mock_repository = MagicMock()
    service = FavoriteService(repository=mock_repository, sw_service=None)

    invalid_favorite = SWFavoriteCreate(
        user_id="user_1_abc",
        sw_id="abc",
        resource="people",
        url="https://swapi.dev/api/people/1/",
        name="Luke Skywalker"
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.add_favorite(invalid_favorite)
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "sw_id deve ser um número inteiro."


@pytest.mark.asyncio
async def test_add_favorite_success():
    mock_repository = MagicMock()
    mock_repository.save = AsyncMock(return_value={
        "id": "fav_1",
        "user_id": "user_1_abc",
        "sw_id": "1",
        "resource": "people",
        "url": "https://swapi.dev/api/people/1/",
        "name": "Luke Skywalker"
    })

    service = FavoriteService(repository=mock_repository, sw_service=None)

    valid_favorite = SWFavoriteCreate(
        user_id="user_1_abc",
        sw_id="1",
        resource="people",
        url="https://swapi.dev/api/people/1/",
        name="Luke Skywalker"
    )

    result = await service.add_favorite(valid_favorite)
    assert result["id"] == "fav_1"
    mock_repository.save.assert_called_once()


@pytest.mark.asyncio
async def test_get_favorite_id_not_found_raises_404():
    mock_repository = MagicMock()
    mock_repository.find_by_id = AsyncMock(return_value=None)

    service = FavoriteService(repository=mock_repository, sw_service=None)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_favorite_id(user_id="user_1_abc", id="fav_1")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Favorito não encontrado."


@pytest.mark.asyncio
async def test_get_favorite_id_wrong_user_raises_404():
    mock_repository = MagicMock()
    mock_repository.find_by_id = AsyncMock(return_value={
        "id": "fav_1",
        "user_id": "user_2_abc"
    })

    service = FavoriteService(repository=mock_repository, sw_service=None)

    with pytest.raises(HTTPException) as exc_info:
        await service.get_favorite_id(user_id="user_1_abc", id="fav_1")
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Favorito não encontrado."


@pytest.mark.asyncio
async def test_get_favorite_id_success_with_details():
    mock_repository = MagicMock()
    mock_repository.find_by_id = AsyncMock(return_value={
        "id": "fav_1",
        "user_id": "user_1_abc",
        "sw_id": "1",
        "resource": "people",
        "url": "https://swapi.dev/api/people/1/",
        "name": "Luke Skywalker"
    })

    mock_sw_service = MagicMock()
    mock_sw_service.get_details = AsyncMock(return_value={
        "name": "Luke Skywalker",
        "height": "172",
        "mass": "77",
        "hair_color": "blond",
        "skin_color": "fair",
        "eye_color": "blue",
        "birth_year": "19BBY",
        "gender": "male",
        "url": "https://swapi.dev/api/people/1/"
    })

    service = FavoriteService(repository=mock_repository, sw_service=mock_sw_service)

    result = await service.get_favorite_id(user_id="user_1_abc", id="fav_1")
    assert result["id"] == "fav_1"
    assert result["details"]["name"] == "Luke Skywalker"
    mock_sw_service.get_details.assert_called_once_with("people", "1")


@pytest.mark.asyncio
async def test_get_favorite_id_success_with_details_error():
    mock_repository = MagicMock()
    mock_repository.find_by_id = AsyncMock(return_value={
        "id": "fav_1",
        "user_id": "user_1_abc",
        "sw_id": "1",
        "resource": "people",
        "url": "https://swapi.dev/api/people/1/",
        "name": "Luke Skywalker"
    })

    mock_sw_service = MagicMock()
    mock_sw_service.get_details = AsyncMock(side_effect=Exception("API Error"))

    service = FavoriteService(repository=mock_repository, sw_service=mock_sw_service)

    result = await service.get_favorite_id(user_id="user_1_abc", id="fav_1")
    assert result["id"] == "fav_1"
    assert "error" in result["details"]
    mock_sw_service.get_details.assert_called_once_with("people", "1")


@pytest.mark.asyncio
async def test_list_favorites_no_filters():
    mock_repository = MagicMock()
    mock_repository.list_with_filters = AsyncMock(return_value=[
        {
            "id": "fav_1",
            "user_id": "user_1_abc",
            "sw_id": "1",
            "resource": "people",
            "url": "https://swapi.dev/api/people/1/",
            "name": "Luke Skywalker"
        },
        {
            "id": "fav_2",
            "user_id": "user_1_abc",
            "sw_id": "2",
            "resource": "people",
            "url": "https://swapi.dev/api/people/2/",
            "name": "C-3PO"
        }
    ])

    service = FavoriteService(repository=mock_repository, sw_service=None)

    result = await service.list_favorites(user_id="user_1_abc")
    assert len(result) == 2
    mock_repository.list_with_filters.assert_called_once_with(
        "favorites",
        filters=[("user_id", "==", "user_1_abc")],
        limit=10,
        last_doc_id=None
    )

@pytest.mark.asyncio
async def test_list_favorites_with_filters():
    mock_repository = MagicMock()
    mock_repository.list_with_filters = AsyncMock(return_value=[
        {
            "id": "fav_2",
            "user_id": "user_1_abc",
            "sw_id": "2",
            "resource": "people",
            "url": "https://swapi.dev/api/people/2/",
            "name": "C-3PO"
        }
    ])

    service = FavoriteService(repository=mock_repository, sw_service=None)

    filters = [("resource", "==", "people")]
    result = await service.list_favorites(user_id="user_1_abc", filters=filters, limit=5, last_id="fav_1")
    assert len(result) == 1
    mock_repository.list_with_filters.assert_called_once_with(
        "favorites",
        filters=[("resource", "==", "people"), ("user_id", "==", "user_1_abc")],
        limit=5,
        last_doc_id="fav_1"
    )


