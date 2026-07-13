from sun_set.constants.project_defaults import (
    DEFAULT_WEEKDAY_1,
    DEFAULT_WEEKDAY_2,
)
from sun_set.models.city import City
from sun_set.models.project_data import ProjectData
from sun_set.models.sunset import (
    MonthData,
    Source,
    SunsetEntry,
    YearData,
)
from sun_set.services.project_workflow import (
    ProjectLoadError,
    ProjectLoadSuccess,
    ProjectSaveSuccess,
    execute_project_load,
    execute_project_save,
)
from sun_set.storage.json_storage import read_json, write_json


def test_project_save_and_load_roundtrip(tmp_path):
    project = ProjectData(
        year=2027,
        weekday1=4,
        weekday2=5,
        cities=[
            City(
                name="Amsterdam",
                region="North Holland",
                lat=52.37,
                lon=4.89,
                timezone="Europe/Amsterdam",
                elevation=0,
                sunset_data=YearData(
                    year=2027,
                    source=Source.CALCULATED,
                    hash_before_edit=None,
                    months=None,
                ),
            )
        ],
        export_settings_path="/tmp/export_settings.json",
        export_output_dir="/tmp/export",
    )

    path = tmp_path / "project.json"

    save_result = execute_project_save(project, str(path))
    assert isinstance(save_result, ProjectSaveSuccess)

    load_result = execute_project_load(str(path))
    assert isinstance(load_result, ProjectLoadSuccess)

    loaded_project = load_result.project

    assert loaded_project.cities == project.cities
    assert loaded_project.export_settings_path == project.export_settings_path
    assert loaded_project.export_output_dir == project.export_output_dir


def test_legacy_city_list_migrates_to_project_format(tmp_path):
    legacy_path = tmp_path / "legacy.json"
    migrated_path = tmp_path / "migrated.json"

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

    write_json(legacy_path, legacy_data)

    load_result = execute_project_load(str(legacy_path))

    assert isinstance(load_result, ProjectLoadSuccess)
    assert len(load_result.project.cities) == 1
    assert load_result.project.weekday1 == DEFAULT_WEEKDAY_1
    assert load_result.project.weekday2 == DEFAULT_WEEKDAY_2

    save_result = execute_project_save(
        load_result.project,
        str(migrated_path),
    )

    assert isinstance(save_result, ProjectSaveSuccess)

    saved_data = read_json(migrated_path)

    assert isinstance(saved_data, dict)
    assert "cities" in saved_data
    assert saved_data["cities"][0]["name"] == "Amsterdam"

    reload_result = execute_project_load(str(migrated_path))

    assert isinstance(reload_result, ProjectLoadSuccess)
    assert len(reload_result.project.cities) == 1
    assert reload_result.project.cities[0].name == "Amsterdam"


def test_empty_project_save_and_load_roundtrip(tmp_path):
    project = ProjectData(
        year=2027,
        weekday1=4,
        weekday2=5,
        cities=[],
        export_settings_path=None,
        export_output_dir=None,
    )

    path = tmp_path / "empty_project.json"

    save_result = execute_project_save(project, str(path))

    assert isinstance(save_result, ProjectSaveSuccess)

    load_result = execute_project_load(str(path))

    assert isinstance(load_result, ProjectLoadSuccess)
    assert load_result.project.cities == []
    assert load_result.project.export_settings_path is None
    assert load_result.project.export_output_dir is None


def test_project_with_edited_sunset_data_roundtrip(tmp_path):
    city = City(
        name="Murmansk",
        region="Murmansk Oblast",
        lat=68.97,
        lon=33.08,
        timezone="Europe/Moscow",
        elevation=50,
        sunset_data=YearData(
            year=2027,
            source=Source.EDITED,
            hash_before_edit="saved-hash",
            months=[
                MonthData(
                    month=1,
                    days=[
                        SunsetEntry(
                            day=1,
                            weekday=4,
                            time="14:30",
                            source=Source.EDITED,
                        )
                    ],
                )
            ],
        ),
    )

    project = ProjectData(
        year=2027,
        weekday1=4,
        weekday2=5,
        cities=[city],
        export_settings_path=None,
        export_output_dir=None,
    )

    path = tmp_path / "edited_project.json"

    save_result = execute_project_save(project, str(path))
    assert isinstance(save_result, ProjectSaveSuccess)

    load_result = execute_project_load(str(path))
    assert isinstance(load_result, ProjectLoadSuccess)

    loaded_city = load_result.project.cities[0]

    assert loaded_city.sunset_data.source == Source.EDITED
    assert loaded_city.sunset_data.hash_before_edit == "saved-hash"
    assert loaded_city.sunset_data.months is not None

    loaded_month = loaded_city.sunset_data.months[0]
    assert loaded_month.month == 1
    assert len(loaded_month.days) == 1

    loaded_entry = loaded_month.days[0]
    assert loaded_entry.day == 1
    assert loaded_entry.weekday == 4
    assert loaded_entry.time == "14:30"
    assert loaded_entry.source == Source.EDITED


def test_invalid_project_json_returns_load_error(tmp_path):
    path = tmp_path / "broken_project.json"
    path.write_text("{ invalid json", encoding="utf-8")

    result = execute_project_load(str(path))

    assert isinstance(result, ProjectLoadError)
    assert result.message == "Ошибка: файл не является корректным JSON."


def test_missing_project_file_returns_load_error(tmp_path):
    path = tmp_path / "missing_project.json"

    result = execute_project_load(str(path))

    assert isinstance(result, ProjectLoadError)
    assert result.message == ("Ошибка: Файл не найден. Проверьте путь к файлу.")
