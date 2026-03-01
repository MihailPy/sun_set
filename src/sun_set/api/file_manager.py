import json
from dataclasses import asdict
from enum import Enum

from dacite import Config, from_dict

from sun_set.models.city import City


def custom_asdict_factory(data):
    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.value
        return obj

    return {k: convert_value(v) for k, v in data}


def save_to_json(cities: list[City], filename: str):  # noqa: F821
    with open(filename, "w") as f:
        data_to_save = [asdict(c, dict_factory=custom_asdict_factory) for c in cities]
        json.dump(data_to_save, f, ensure_ascii=False, indent=4)


def load_from_json(filename: str) -> tuple[list[City] | None, str | None]:
    try:
        with open(filename) as f:
            data_list = json.load(f)
            config = Config(cast=[Enum])
            cities = [
                from_dict(data_class=City, data=item, config=config)
                for item in data_list
            ]
            return cities, None
    except FileNotFoundError:
        return None, "Ошибка: Файл не найден. Проверьте путь к файлу."

    except json.JSONDecodeError:
        return None, "Ошибка: Файл поврежден или имеет неверный формат JSON."

    except PermissionError:
        return None, "Ошибка: Нет прав доступа для чтения этого файла."

    except TypeError as e:
        return None, f"Ошибка в структуре данных файла: {e}"
