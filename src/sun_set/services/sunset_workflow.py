from dataclasses import dataclass

from sun_set.models.city import City
from sun_set.services.city_service import (
    create_default_city,
    update_cities_sunset,
    update_city_sunset,
)


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


@dataclass(frozen=True)
class SingleCitySunsetUpdateRequest:
    city: City
    settings: SunsetSettings


def build_single_city_sunset_update_request(
    city: City,
    settings: SunsetSettings,
) -> SingleCitySunsetUpdateRequest:
    return SingleCitySunsetUpdateRequest(
        city=city,
        settings=settings,
    )


def execute_single_city_sunset_update(
    request: SingleCitySunsetUpdateRequest,
) -> None:
    update_city_sunset(
        request.city,
        request.settings.year,
        request.settings.weekday1,
        request.settings.weekday2,
    )


def create_city_for_year(year: int) -> City:
    return create_default_city(year)
