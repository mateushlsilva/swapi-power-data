from typing import Optional
from fastapi import HTTPException
from app.repository.firestore_repository import FirestoreRepository
from app.schemas.favorites.sw_favorites import SWFavoriteCreate
from app.services.starwars_service import StarWarsService

class FavoriteService:
    def __init__(self, repository: FirestoreRepository, sw_service: Optional[StarWarsService] = None):
        self.sw_service = sw_service
        self.repository = repository
        

    async def get_favorite_id(self, user_id: str, id: str):
        favorite = await self.repository.find_by_id("favorites", id)
        if not favorite or favorite.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Favorito não encontrado.")
        try:
            details = await self.sw_service.get_details(favorite.get('resource'), favorite.get('sw_id'))
            favorite['details'] = details or {}
        except Exception:
            favorite['details'] = {"error": "Não foi possível carregar os detalhes da Star Wars API no momento."}
        return favorite

    async def list_favorites(self, user_id: str, filters: list[tuple] = None, limit: int = 10, last_id: Optional[str] = None):
        if not filters:
            filters = [("user_id", "==", user_id)]
        else:
            filters.append(("user_id", "==", user_id))
        return await self.repository.list_with_filters("favorites", filters=filters, limit=limit, last_doc_id=last_id)

    async def add_favorite(self, favorite_create: SWFavoriteCreate):
        if not favorite_create.url.startswith("https://"):
            raise HTTPException(status_code=400, detail="URL inválida. Deve começar com 'https://'")
        if not favorite_create.sw_id.isdigit():
            raise HTTPException(status_code=400, detail="sw_id deve ser um número inteiro.")
        return await self.repository.save(
            collection="favorites", 
            data=favorite_create.model_dump()
        )
    
    async def remove_favorite(self, favorite_id: str, user_id: str):
        favorite = await self.repository.find_by_id("favorites", favorite_id)
        if not favorite or favorite.get("user_id") != user_id:
            raise HTTPException(status_code=404, detail="Favorito não encontrado.")
        return await self.repository.delete(
            collection="favorites",
            doc_id=favorite_id
        )