from sun_set.models.city import City
from sun_set.models.project_data import ProjectData
from sun_set.models.sunset import Source, YearData
from sun_set.storage.city_json_storage import (
    load_cities_from_json,
    load_project_from_json,
    save_cities_to_json,
    save_project_to_json,
)


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
    assert loaded_project.year == 2027
    assert loaded_project.weekday1 == 4
    assert loaded_project.weekday2 == 5
    assert loaded_project.cities == []
    assert loaded_project.export_settings_path == "/tmp/export_settings.json"
    assert loaded_project.export_output_dir == "/tmp/export"
