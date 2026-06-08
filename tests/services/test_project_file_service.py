from unittest.mock import Mock, patch

from sun_set.models.project_data import ProjectData
from sun_set.services.project_file_service import (
    load_project,
    save_project,
)


@patch("sun_set.services.project_file_service.load_project_from_json")
def test_load_project(mock_load):
    mock_load.return_value = (Mock(spec=ProjectData), None)

    load_project("project.json")

    mock_load.assert_called_once_with("project.json")


@patch("sun_set.services.project_file_service.save_project_to_json")
def test_save_project(mock_save):
    project = Mock(spec=ProjectData)

    save_project(project, "project.json")

    mock_save.assert_called_once_with(
        project,
        "project.json",
    )
