from sun_set.core.astronomy import get_city_sunset
from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData


def create_default_city(year: int) -> City:
    return City(
        name="Новый город",
        region="-",
        lat=0.0,
        lon=0.0,
        timezone="UTC",
        elevation=0,
        sunset_data=YearData(
            year=year,
            source=Source.CALCULATED,
            hash_before_edit=None,
            months=None,
        ),
    )


def update_city_sunset(
    city: City,
    year: int,
    weekday1: int,
    weekday2: int,
) -> None:
    city.sunset_data = get_city_sunset(city, year, weekday1, weekday2)
    city.sunset_data.hash_before_edit = city.get_stable_hash()


def update_cities_sunset(
    cities: list[City],
    year: int,
    weekday1: int,
    weekday2: int,
) -> None:
    for city in cities:
        update_city_sunset(city, year, weekday1, weekday2)
