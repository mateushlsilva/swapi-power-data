from pydantic import BaseModel

class SWFilms(BaseModel):
    title: str
    episode_id: int
    opening_crawl: str
    director: str
    producer: str
    release_date: str
    created: str
    edited: str
    url: str

class SWFilmsDetails(SWFilms):
    characters: list[str]
    planets: list[str]
    starships: list[str]
    vehicles: list[str]
    species: list[str]