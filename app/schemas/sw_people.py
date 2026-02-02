from pydantic import BaseModel

class SWPeople(BaseModel):
    name: str
    height: str
    mass: str
    hair_color: str
    skin_color: str
    eye_color: str
    birth_year: str
    gender: str
    created: str
    edited: str
    url: str

class SWPeopleDetails(SWPeople):
    films: list[str]
    species: list[str]
    starships: list[str]
    vehicles: list[str]
    homeworld: str