from pydantic import BaseModel
from app.schemas.sw.sw_resouce import SWResource

class Favorite(BaseModel):
    user_id: str
    sw_id:str
    resource: SWResource
    url: str
    name: str
