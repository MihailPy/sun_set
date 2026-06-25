from unittest.mock import Mock, patch

from sun_set.services.project_workflow import (
    ProjectLoadError,
    ProjectLoadSuccess,
    execute_project_load,
)


@patch("sun_set.services.project_workflow.load_project")
def test_execute_project_load_success(mock_load_project):
    project = Mock()
    mock_load_project.return_value = (project, None)

    result = execute_project_load("project.json")

    assert isinstance(result, ProjectLoadSuccess)
    assert result.project == project


@patch("sun_set.services.project_workflow.load_project")
def test_execute_project_load_error(mock_load_project):
    mock_load_project.return_value = (None, "Ошибка загрузки")

    result = execute_project_load("project.json")

    assert isinstance(result, ProjectLoadError)
    assert result.message == "Ошибка загрузки"


@patch("sun_set.services.project_workflow.load_project")
def test_execute_project_load_empty_result(mock_load_project):
    mock_load_project.return_value = (None, None)

    result = execute_project_load("project.json")

    assert isinstance(result, ProjectLoadError)
    assert result.message == "Не удалось загрузить проект."
