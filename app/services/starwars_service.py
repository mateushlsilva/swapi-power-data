from app.integration.SwapiClient import SwapiClient
from redis.asyncio import Redis
from fastapi import HTTPException
import httpx

class StarWarsService:
    def __init__(self, swapi_client: SwapiClient, redis: Redis):
        self.swapi = swapi_client
        self.redis = redis
        self.failure_key = "circuit:swapi:failures"
        self.status_key = "circuit:swapi:status" # open ou closed
        self.threshold = 3
        self.recovery_time = 60

    async def get_circuit(self, resource: str, **kwargs):
        status = await self.redis.get(self.status_key)
        if status == "open":
            raise HTTPException(
                status_code=503, 
                detail="Circuito aberto: SWAPI temporariamente bloqueada."
            )
        try:
            method = getattr(self.swapi, resource) # pega o método do SWAPI ex: people, planets
            data = await method(**kwargs) # passa os argumentos como name , page
            
            await self.redis.delete(self.failure_key)
            return data

        except Exception as e:
            failures = await self.redis.incr(self.failure_key)
            
            if failures >= self.threshold:
                await self.redis.set(self.status_key, "open", ex=self.recovery_time)
                print(f"CIRCUITO ABERTO para SWAPI")

            if isinstance(e, httpx.HTTPStatusError):
                raise HTTPException(
                    status_code=e.response.status_code,
                    detail="Recurso não encontrado" if e.response.status_code == 404 else e.response.json()
                )
            elif isinstance(e, httpx.RequestError):
                raise HTTPException(
                    status_code=504,
                    detail="Tempo de resposta da SWAPI esgotado (Timeout)."
                )
            
            
            raise HTTPException(status_code=500, detail=str(e))