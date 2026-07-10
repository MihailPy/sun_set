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
def test_execute_project_save_permission_error(mock_save_project):
    project = Mock()
    mock_save_project.side_effect = PermissionError

    result = execute_project_save(project, "project.json")

    assert isinstance(result, ProjectSaveError)
    assert result.message == ("Нет прав для сохранения файла в выбранное место.")


@patch("sun_set.services.project_workflow.save_project")
def test_execute_project_save_directory_error(mock_save_project):
    project = Mock()
    mock_save_project.side_effect = IsADirectoryError

    result = execute_project_save(project, "project.json")

    assert isinstance(result, ProjectSaveError)
    assert result.message == "Вместо файла указан путь к папке."


@patch("sun_set.services.project_workflow.save_project")
def test_execute_project_save_os_error(mock_save_project):
    project = Mock()
    mock_save_project.side_effect = OSError("Диск недоступен")

    result = execute_project_save(project, "project.json")

    assert isinstance(result, ProjectSaveError)
    assert result.message == "Не удалось сохранить проект: Диск недоступен"


@patch("sun_set.services.project_workflow.save_project")
def test_execute_project_save_unexpected_error(mock_save_project):
    project = Mock()
    mock_save_project.side_effect = RuntimeError("Неизвестная ошибка")

    result = execute_project_save(project, "project.json")

    assert isinstance(result, ProjectSaveError)
    assert result.message == (
        "Непредвиденная ошибка при сохранении проекта: Неизвестная ошибка"
    )


def test_execute_project_save_empty_path():
    project = Mock()

    result = execute_project_save(project, "")

    assert isinstance(result, ProjectSaveError)
