from dataclasses import asdict
from datetime import datetime
from enum import Enum
from pathlib import Path

from dacite import Config, DaciteError, from_dict

from sun_set.models.city import City
from sun_set.models.project_data import ProjectData
from sun_set.storage.json_storage import read_json, write_json


def save_project_to_json(
    project: ProjectData,
    filename: str,
) -> None:
    data_to_save = asdict(
        project,
        dict_factory=custom_asdict_factory,
    )

    write_json(Path(filename), data_to_save)


def load_project_from_json(
    file_path: str,
) -> tuple[ProjectData | None, str | None]:
    try:
        data = read_json(Path(file_path))

        config = Config(cast=[Enum])

        if isinstance(data, list):
            return (
                ProjectData(
                    year=datetime.now().year,
                    weekday1=5,
                    weekday2=6,
                    cities=[
                        from_dict(
                            data_class=City,
                            data=item,
                            config=config,
                        )
                        for item in data
                        if isinstance(item, dict)
                    ],
                ),
                None,
            )

        project = from_dict(
            data_class=ProjectData,
            data=data,
            config=config,
        )

        return project, None

    except FileNotFoundError:
        return None, "Ошибка: Файл не найден. Проверьте путь к файлу."
    except DaciteError as error:
        return None, f"Ошибка в структуре данных файла: {error}"
    except Exception as error:
        return None, f"Ошибка при чтении JSON-файла: {error}"


def custom_asdict_factory(data):
    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.value
        return obj

    return {key: convert_value(value) for key, value in data}


def save_cities_to_json(cities: list[City], filename: str) -> None:
    data_to_save = [asdict(city, dict_factory=custom_asdict_factory) for city in cities]

    write_json(Path(filename), data_to_save)


def load_cities_from_json(file_path: str) -> tuple[list[City] | None, str | None]:
    try:
        data_list = read_json(Path(file_path))
        config = Config(cast=[Enum])

        cities = [
            from_dict(data_class=City, data=item, config=config)
            for item in data_list
            if isinstance(item, dict)
        ]

        return cities, None

    except FileNotFoundError:
        return None, "Ошибка: Файл не найден. Проверьте путь к файлу."
    except DaciteError as error:
        return None, f"Ошибка в структуре данных файла: {error}"
    except Exception as error:
        return None, f"Ошибка при чтении JSON-файла: {error}"
