from sun_set.api.file_manager import load_from_json, save_to_json
from sun_set.models.city import City


def load_cities_from_file(file_path: str) -> tuple[list[City] | None, str | None]:
    return load_from_json(file_path)


def save_cities_to_file(cities: list[City], file_path: str) -> None:
    save_to_json(cities, file_path)
