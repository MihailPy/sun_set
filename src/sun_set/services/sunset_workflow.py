from dataclasses import dataclass

from sun_set.models.city import City
from sun_set.services.city_service import update_cities_sunset


@dataclass(frozen=True)
class SunsetSettings:
    year: int
    weekday1: int
    weekday2: int


@dataclass(frozen=True)
class SunsetUpdateRequest:
    cities: list[City]
    settings: SunsetSettings


def build_sunset_update_request(
    cities: list[City],
    settings: SunsetSettings,
) -> SunsetUpdateRequest:
    return SunsetUpdateRequest(
        cities=cities,
        settings=settings,
    )


def execute_sunset_update(request: SunsetUpdateRequest) -> None:
    update_cities_sunset(
        request.cities,
        request.settings.year,
        request.settings.weekday1,
        request.settings.weekday2,
    )
