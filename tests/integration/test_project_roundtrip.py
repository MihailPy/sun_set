from sun_set.constants.project_defaults import (
    DEFAULT_WEEKDAY_1,
    DEFAULT_WEEKDAY_2,
)
from sun_set.models.city import City
from sun_set.models.project_data import ProjectData
from sun_set.models.sunset import Source, YearData
from sun_set.services.project_workflow import (
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
