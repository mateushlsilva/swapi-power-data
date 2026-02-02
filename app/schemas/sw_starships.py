from pydantic import BaseModel

class SWStarships(BaseModel):
    name: str
    model: str
    manufacturer: str
    cost_in_credits: str
    length: str
    max_atmosphering_speed: str
    crew: str
    passengers: str
    cargo_capacity: str
    consumables: str
    hyperdrive_rating: str
    MGLT: str
    starship_class: str
    created: str
    edited: str
    url: str


class SWStarshipsDetails(SWStarships):
    pilots: list[str]
    films: list[str]