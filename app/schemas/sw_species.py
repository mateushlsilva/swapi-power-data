from pydantic import BaseModel

class SWSpecies(BaseModel):
    name: str
    classification: str
    designation: str
    average_height: str
    skin_colors: str
    hair_colors: str
    eye_colors: str
    average_lifespan: str
    language: str
    created: str
    edited: str
    url: str


class SWSpeciesDetails(SWSpecies):
    homeworld: str | None
    people: list[str]
    films: list[str]