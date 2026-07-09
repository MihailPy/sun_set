from sun_set.constants.project_defaults import (
    DEFAULT_WEEKDAY_1,
    DEFAULT_WEEKDAY_2,
    get_default_project_year,
)
from sun_set.models.city import City
from sun_set.models.project_data import ProjectData
from sun_set.models.sunset import Source, YearData
from sun_set.storage.city_json_storage import (
    load_cities_from_json,
    load_project_from_json,
    save_cities_to_json,
    save_project_to_json,
)
from sun_set.storage.json_storage import write_json


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


def test_load_old_city_list_format(tmp_path):
    path = tmp_path / "cities.json"

    path.write_text(
        """
        [
            {
                "name": "Amsterdam",
                "region": "North Holland",
                "lat": 52.37,
                "lon": 4.89,
                "timezone": "Europe/Amsterdam",
                "elevation": 0,
                "sunset_data": {
                    "year": 2025,
                    "source": 1,
                    "hash_before_edit": null,
                    "months": null
                }
            }
        ]
        """,
        encoding="utf-8",
    )

    project, error = load_project_from_json(str(path))

    assert error is None
    assert project is not None
    assert len(project.cities) == 1


def test_save_and_load_project_export_paths(tmp_path):
    project = ProjectData(
        year=2026,
        weekday1=4,
        weekday2=5,
        cities=[],
        export_settings_path="/tmp/export_settings.json",
        export_output_dir="/tmp/export",
    )

    path = tmp_path / "project.json"

    save_project_to_json(project, str(path))
    loaded_project, error = load_project_from_json(str(path))

    assert error is None
    assert loaded_project is not None
    assert loaded_project.export_settings_path == "/tmp/export_settings.json"
    assert loaded_project.export_output_dir == "/tmp/export"


def test_save_and_load_project_json(tmp_path):
    project = ProjectData(
        year=2027,
        weekday1=4,
        weekday2=5,
        cities=[],
        export_settings_path="/tmp/export_settings.json",
        export_output_dir="/tmp/export",
    )

    path = tmp_path / "project.json"

    save_project_to_json(project, str(path))
    loaded_project, error = load_project_from_json(str(path))

    assert error is None
    assert loaded_project is not None
    assert loaded_project.year == get_default_project_year()
    assert loaded_project.weekday1 == DEFAULT_WEEKDAY_1
    assert loaded_project.weekday2 == DEFAULT_WEEKDAY_2
    assert loaded_project.cities == []
    assert loaded_project.export_settings_path == "/tmp/export_settings.json"
    assert loaded_project.export_output_dir == "/tmp/export"


def test_load_legacy_city_list_as_project(tmp_path):
    legacy_data = [
        {
            "name": "Amsterdam",
            "region": "North Holland",
            "lat": 52.37,
            "lon": 4.89,
            "timezone": "Europe/Amsterdam",
            "elevation": 0,
            "sunset_data": {
                "year": 2027,
                "source": Source.CALCULATED.value,
                "hash_before_edit": None,
                "months": None,
            },
        }
    ]

    path = tmp_path / "legacy_cities.json"
    write_json(path, legacy_data)

    project, error = load_project_from_json(str(path))

    assert error is None
    assert project is not None
    assert project.cities[0].name == "Amsterdam"
    assert project.weekday1 == DEFAULT_WEEKDAY_1
    assert project.weekday2 == DEFAULT_WEEKDAY_2


def test_load_project_from_invalid_json(tmp_path):
    path = tmp_path / "broken.json"
    path.write_text("{ broken json", encoding="utf-8")

    project, error = load_project_from_json(str(path))

    assert project is None
    assert error is not None
    assert "Ошибка при чтении JSON-файла" in error


def test_load_project_from_empty_file(tmp_path):
    path = tmp_path / "empty.json"
    path.write_text("", encoding="utf-8")

    project, error = load_project_from_json(str(path))

    assert project is None
    assert error is not None
    assert "Ошибка при чтении JSON-файла" in error


def test_load_project_from_missing_file(tmp_path):
    path = tmp_path / "missing.json"

    project, error = load_project_from_json(str(path))

    assert project is None
    assert error == "Ошибка: Файл не найден. Проверьте путь к файлу."


def test_load_project_from_invalid_project_structure(tmp_path):
    path = tmp_path / "invalid_project.json"
    write_json(
        path,
        {
            "version": "not-a-number",
            "cities": "not-a-list",
        },
    )

    project, error = load_project_from_json(str(path))

    assert project is None
    assert error is not None
    assert "Ошибка в структуре данных файла" in error


def test_load_legacy_city_list_with_invalid_city_structure(tmp_path):
    path = tmp_path / "legacy_invalid_city.json"
    write_json(
        path,
        [
            {
                "name": "Amsterdam",
                "lat": "not-a-number",
            }
        ],
    )

    project, error = load_project_from_json(str(path))

    assert project is None
    assert error is not None
    assert "Ошибка в структуре данных файла" in error
