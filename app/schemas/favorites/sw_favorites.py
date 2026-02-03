from pydantic import BaseModel
from app.schemas.sw.sw_resouce import SWResource
from app.schemas.sw.sw import SWAnyDetailsRead

class SWFavoriteRequestCreate(BaseModel):
    sw_id: str
    resource: SWResource
    url: str
    name: str

class SWFavoriteCreate(SWFavoriteRequestCreate):
    user_id: str

class SWFavorite(SWFavoriteCreate):
    id: str


class SWFavoriteRead(SWFavorite):
    details: SWAnyDetailsRead | dict