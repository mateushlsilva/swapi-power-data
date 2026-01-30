from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import httpx
from config import settings


class SwapiClient:
    def __init__(self):
        self.base_url = settings.SWAPI_BASE
        self.timeout = httpx.Timeout(10.0)

    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=6),
        retry=retry_if_exception_type(httpx.RequestError),
        reraise=True
    )
    async def get_api(self, endpoint: str, name: str = None, page: int = None):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {}
            if name: params["search"] = name
            if page: params["page"] = page
            response = await client.get(
                f"{self.base_url}/{endpoint}",
                params=params
            )
            response.raise_for_status()
            return response.json()


    async def films(self, name: str = None, page: int = None):
        return await self.get_api("films", name=name, page=page)

    async def people(self, name: str = None, page: int = None):
        return await self.get_api("people", name=name, page=page)

    async def planets(self, name: str = None, page: int = None):
        return await self.get_api("planets", name=name, page=page)

    async def species(self, name: str = None, page: int = None):
        return await self.get_api("species", name=name, page=page)

    async def starships(self, name: str = None, page: int = None):
        return await self.get_api("starships", name=name, page=page)

    async def vehicles(self, name: str = None, page: int = None):
        return await self.get_api("vehicles", name=name, page=page)
