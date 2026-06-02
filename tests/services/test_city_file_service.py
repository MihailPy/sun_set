from unittest.mock import patch

from sun_set.services.city_file_service import (
    load_cities_from_file,
    save_cities_to_file,
)


@patch("sun_set.services.city_file_service.load_from_json")
def test_load_cities_from_file(mock_load_from_json):
    mock_load_from_json.return_value = ([], None)

    result = load_cities_from_file("cities.json")

    assert result == ([], None)
    mock_load_from_json.assert_called_once_with("cities.json")


@patch("sun_set.services.city_file_service.save_to_json")
def test_save_cities_to_file(mock_save_to_json):
    cities = []

    save_cities_to_file(cities, "cities.json")

    mock_save_to_json.assert_called_once_with(cities, "cities.json")
