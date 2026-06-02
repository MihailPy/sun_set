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
