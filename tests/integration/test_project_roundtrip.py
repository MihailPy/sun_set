from sun_set.models.city import City
from sun_set.models.project_data import ProjectData
from sun_set.models.sunset import Source, YearData
from sun_set.services.project_workflow import (
    ProjectLoadSuccess,
    ProjectSaveSuccess,
    execute_project_load,
    execute_project_save,
)


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
