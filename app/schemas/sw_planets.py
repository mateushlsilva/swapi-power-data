from pydantic import BaseModel

class SWPlanets(BaseModel):
    name: str
    rotation_period: str
    orbital_period: str
    diameter: str
    climate: str
    gravity: str
    terrain: str
    surface_water: str
    population: str
    created: str
    edited: str
    url: str


class SWPlanetsDetails(SWPlanets):
    residents: list[str]
    films: list[str]
