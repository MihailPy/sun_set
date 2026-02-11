import json

from sun_set.models.city import City


def save_to_json(cities: list[City], filename: str):  # noqa: F821
    with open(filename, "w") as f:
        json.dump([vars(c) for c in cities], f)


def load_from_json(filename: str) -> tuple[list[City] | None, str | None]:
    try:
        with open(filename) as f:
            return [City(**data) for data in json.load(f)], None
    except FileNotFoundError:
        return None, "Ошибка: Файл не найден. Проверьте путь к файлу."

    except json.JSONDecodeError:
        return None, "Ошибка: Файл поврежден или имеет неверный формат JSON."

    except PermissionError:
        return None, "Ошибка: Нет прав доступа для чтения этого файла."

    except Exception as e:
        return None, f"Неизвестная ошибка: {e}"
