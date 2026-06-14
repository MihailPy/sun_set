from sun_set.models.project_data import ProjectData
from sun_set.services.project_state_service import build_project_data


def test_build_project_data():
    project = build_project_data(
        year=2027,
        weekday1=4,
        weekday2=5,
        cities=[],
        export_settings_path="/tmp/export_settings.json",
        export_output_dir="/tmp/export",
    )

    assert isinstance(project, ProjectData)
    assert project.year == 2027
    assert project.weekday1 == 4
    assert project.weekday2 == 5
    assert project.cities == []
    assert project.export_settings_path == "/tmp/export_settings.json"
    assert project.export_output_dir == "/tmp/export"


def test_build_project_data_converts_empty_paths_to_none():
    project = build_project_data(
        year=2027,
        weekday1=4,
        weekday2=5,
        cities=[],
        export_settings_path="",
        export_output_dir="",
    )

    assert project.export_settings_path is None
    assert project.export_output_dir is None
