from unittest.mock import Mock, patch

from sun_set.services.project_workflow import (
    ProjectLoadError,
    ProjectLoadSuccess,
    ProjectSaveError,
    ProjectSaveSuccess,
    execute_project_load,
    execute_project_save,
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


@patch("sun_set.services.project_workflow.save_project")
def test_execute_project_save_success(mock_save_project):
    project = Mock()

    result = execute_project_save(project, "project.json")

    assert isinstance(result, ProjectSaveSuccess)
    assert result.file_path == "project.json"
    mock_save_project.assert_called_once_with(project, "project.json")


@patch("sun_set.services.project_workflow.save_project")
def test_execute_project_save_error(mock_save_project):
    project = Mock()
    mock_save_project.side_effect = RuntimeError("Нет доступа")

    result = execute_project_save(project, "project.json")

    assert isinstance(result, ProjectSaveError)
    assert result.message == "Нет доступа"
