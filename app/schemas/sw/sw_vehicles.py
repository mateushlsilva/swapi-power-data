from pydantic import BaseModel

class SWVehicles(BaseModel):
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
    vehicle_class: str
    created: str
    edited: str
    url: str


class SWVehiclesDetails(SWVehicles):
    pilots: list[str]
    films: list[str]