from dataclasses import dataclass

from sun_set.models.city import City


@dataclass(frozen=True)
class SunsetUpdateRequest:
    cities: list[City]
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
