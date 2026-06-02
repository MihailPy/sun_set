from unittest.mock import Mock, patch

from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData
from sun_set.services.city_service import (
    create_default_city,
    update_cities_sunset,
    update_city_sunset,
)


def test_create_default_city():
    city = create_default_city(2026)

    assert isinstance(city, City)
    assert city.name == "Новый город"
    assert city.region == "-"
    assert city.lat == 0.0
    assert city.lon == 0.0
    assert city.timezone == "UTC"
    assert city.elevation == 0
    assert city.sunset_data.year == 2026
    assert city.sunset_data.source == Source.CALCULATED
    assert city.sunset_data.hash_before_edit is None
    assert city.sunset_data.months is None


@patch("sun_set.services.city_service.get_city_sunset")
def test_update_city_sunset(mock_get_city_sunset):
    city = create_default_city(2026)
    sunset_data = Mock(spec=YearData)
    mock_get_city_sunset.return_value = sunset_data

    update_city_sunset(city, 2027, 4, 5)

    mock_get_city_sunset.assert_called_once_with(city, 2027, 4, 5)
    assert city.sunset_data == sunset_data
    assert city.sunset_data.hash_before_edit == city.get_stable_hash()


@patch("sun_set.services.city_service.get_city_sunset")
def test_update_cities_sunset(mock_get_city_sunset):
    city_1 = create_default_city(2026)
    city_2 = create_default_city(2026)

    sunset_data_1 = Mock(spec=YearData)
    sunset_data_2 = Mock(spec=YearData)
    mock_get_city_sunset.side_effect = [sunset_data_1, sunset_data_2]

    update_cities_sunset([city_1, city_2], 2027, 4, 5)

    assert mock_get_city_sunset.call_count == 2
    assert city_1.sunset_data == sunset_data_1
    assert city_2.sunset_data == sunset_data_2
    assert city_1.sunset_data.hash_before_edit == city_1.get_stable_hash()
    assert city_2.sunset_data.hash_before_edit == city_2.get_stable_hash()
