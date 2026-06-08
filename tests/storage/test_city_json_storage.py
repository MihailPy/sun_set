from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData
from sun_set.storage.city_json_storage import (
    load_cities_from_json,
    save_cities_to_json,
)


def test_save_and_load_cities_json(tmp_path):
    city = City(
        name="Test City",
        region="Test Region",
        lat=10.5,
        lon=20.5,
        timezone="UTC",
        elevation=100,
        sunset_data=YearData(
            year=2026,
            source=Source.CALCULATED,
            hash_before_edit=None,
            months=None,
        ),
    )

    path = tmp_path / "cities.json"

    save_cities_to_json([city], str(path))
    cities, error = load_cities_from_json(str(path))

    assert error is None
    assert cities is not None
    assert len(cities) == 1

    loaded_city = cities[0]
    assert loaded_city.name == city.name
    assert loaded_city.region == city.region
    assert loaded_city.lat == city.lat
    assert loaded_city.lon == city.lon
    assert loaded_city.timezone == city.timezone
    assert loaded_city.elevation == city.elevation
    assert loaded_city.sunset_data.year == 2026
    assert loaded_city.sunset_data.source == Source.CALCULATED
