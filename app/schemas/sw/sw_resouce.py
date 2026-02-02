from enum import Enum

class SWResource(str, Enum):
    films: str = "films"
    people: str = "people"
    planets: str = "planets"
    species: str = "species"
    starships: str = "starships"
    vehicles: str = "vehicles"


