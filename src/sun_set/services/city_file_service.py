from sun_set.models.city import City
from sun_set.storage.city_json_storage import load_cities_from_json, save_cities_to_json


def load_cities_from_file(file_path: str) -> tuple[list[City] | None, str | None]:
    return load_cities_from_json(file_path)


def save_cities_to_file(cities: list[City], file_path: str) -> None:
    save_cities_to_json(cities, file_path)
