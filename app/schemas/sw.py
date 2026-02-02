from pydantic import BaseModel, RootModel
from typing import Union
from app.schemas.sw_people import SWPeople, SWPeopleDetails
from app.schemas.sw_films import SWFilms, SWFilmsDetails
from app.schemas.sw_planets import SWPlanets, SWPlanetsDetails
from app.schemas.sw_species import SWSpecies, SWSpeciesDetails
from app.schemas.sw_starships import SWStarships, SWStarshipsDetails
from app.schemas.sw_vehicles import SWVehicles, SWVehiclesDetails

class SWRead(BaseModel):
    count: int
    next: str | None
    previous: str | None

class SWPeopleRead(SWRead):
    results: list[SWPeople]

class SWFilmsRead(SWRead):
    results: list[SWFilms]

class SWPlanetsRead(SWRead):
    results: list[SWPlanets]

class SWSpeciesRead(SWRead):
    results: list[SWSpecies]

class SWStarshipsRead(SWRead):
    results: list[SWStarships]

class SWVehiclesRead(SWRead):
    results: list[SWVehicles]


class SWAnyDetailsRead(RootModel):
    root: Union[
        SWPeopleDetails, 
        SWFilmsDetails, 
        SWPlanetsDetails, 
        SWSpeciesDetails, 
        SWStarshipsDetails, 
        SWVehiclesDetails
    ]