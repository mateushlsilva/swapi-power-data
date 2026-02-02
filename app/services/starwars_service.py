from app.integration.SwapiClient import SwapiClient
from app.core.config import settings
from app.schemas.sw_resouce import SWResource
from redis.asyncio import Redis
from fastapi import HTTPException
import httpx
import json
import asyncio

class StarWarsService:
    def __init__(self, swapi_client: SwapiClient, redis: Redis):
        self.swapi = swapi_client
        self.redis = redis
        self.failure_key = "circuit:swapi:failures"
        self.status_key = "circuit:swapi:status" # open ou closed
        self.threshold = 3
        self.recovery_time = 60
        self.cache_expiry = 3600
        self.cache_expiry_resource = 86400
        self.base_url = settings.SWAPI_BASE


    async def _execute_with_resilience(self, cache_key: str, swapi_callback):
        status = await self.redis.get(self.status_key)
        if status == "open":
            raise HTTPException(
                status_code=503, 
                detail="Circuito aberto: SWAPI temporariamente bloqueada."
            )
        cached_data = await self.redis.get(cache_key)
        if cached_data: return json.loads(cached_data)
        
        try:
            data = await swapi_callback()
            await self.redis.set(cache_key, json.dumps(data), ex=self.cache_expiry)
            await self.redis.delete(self.failure_key)
            return data

        except Exception as e:
            
            if isinstance(e, httpx.HTTPStatusError):
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail="Recurso não encontrado" if e.response.status_code == 404 else e.response.json()
                )
            
            failures = await self.redis.incr(self.failure_key)
            
            if failures >= self.threshold:
                await self.redis.set(self.status_key, "open", ex=self.recovery_time)
                print(f"CIRCUITO ABERTO para SWAPI")

            
            if isinstance(e, httpx.RequestError):
                raise HTTPException(
                    status_code=504,
                    detail="Tempo de resposta da SWAPI esgotado (Timeout)."
                )
            
            
            raise HTTPException(status_code=500, detail=str(e))


    async def _update_resources(self, urls: list[str]):
        async def fetch(url):
            cache_key = f"resource:{url}"
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                return cached_data.decode('utf-8') if isinstance(cached_data, bytes) else cached_data
            try:
                data = await self.swapi.get_url(url)
                name = data.get("name") or data.get("title") or "Unknown"
                await self.redis.set(cache_key, name, ex=self.cache_expiry_resource)
                return name
            except:
                return None
        
        return await asyncio.gather(*[fetch(url) for url in urls])
    

    async def _update_nested_resources(self, data: dict):
        keys_to_update = []
        tasks = []

        for key, value in data.items():
            if isinstance(value, list) and len(value) > 0 and str(value[0]).startswith(self.base_url):
                keys_to_update.append(key)
                tasks.append(self._update_resources(value))
            elif isinstance(value, str) and value.startswith(self.base_url) and key not in ["url"]:
                keys_to_update.append(key)
                tasks.append(self._update_resources([value]))
        
        if tasks:
            results = await asyncio.gather(*tasks)
            for i, key in enumerate(keys_to_update):
                if isinstance(data[key], list):
                    data[key] = results[i]
                else:
                    data[key] = results[i][0] if results[i] else data[key]
        return data
    

    def _strip_nested_lists(self, item: dict):
        keys_to_remove = [
            key for key, value in item.items()
            if isinstance(value, list) and (
                len(value) == 0 or (len(value) > 0 and str(value[0]).startswith(self.base_url))
            ) or (isinstance(value, str) and value.startswith(self.base_url) and not key in ["url"])
        ]
        
        for key in keys_to_remove:
            item.pop(key)
        return item

    async def get_resources(self, resource: str, **kwargs):
        
        kwargs_str = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        cache_key = f"cache:{resource}:{kwargs_str}"
                  
        async def fetch_and_strip():

            method = getattr(self.swapi, resource) # pega o método do SWAPI ex: people, planets
            data = await method(**kwargs) # passa os argumentos como name , page
            
            if "results" in data and isinstance(data["results"], list):
                data["results"] = [self._strip_nested_lists(item) for item in data["results"]]
            else:
                data = self._strip_nested_lists(data)
            return data
        return await self._execute_with_resilience(cache_key, fetch_and_strip)

       
        

    async def get_details(self, resource: SWResource, id: str):
        res_name = resource.value if hasattr(resource, 'value') else resource
        cache_key = f"detail:{resource}:{id}"
        async def fetch_details():
            method = getattr(self.swapi, "get_detail")
            data = await method(res_name, id)
            if isinstance(data, dict):
                data = await self._update_nested_resources(data)
            return data
        return await self._execute_with_resilience(cache_key, fetch_details)