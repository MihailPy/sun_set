from dataclasses import dataclass

from sun_set.models.city import City
from sun_set.services.city_service import update_cities_sunset


@dataclass(frozen=True)
class SunsetUpdateRequest:
    cities: list[City]
    year: int
    weekday1: int
    weekday2: int


@dataclass(frozen=True)
class SunsetSettings:
    year: int
    weekday1: int
    weekday2: int


def build_sunset_update_request(
    cities: list[City],
    year: int,
    weekday1: int,
    weekday2: int,
) -> SunsetUpdateRequest:
    return SunsetUpdateRequest(
        cities=cities,
        year=year,
        weekday1=weekday1,
        weekday2=weekday2,
    )


def execute_sunset_update(request: SunsetUpdateRequest) -> None:
    update_cities_sunset(
        request.cities,
        request.year,
        request.weekday1,
        request.weekday2,
    )
