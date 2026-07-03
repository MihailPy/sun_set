from sun_set.services.project_window_state import ProjectWindowState


def test_project_window_state_without_file():
    state = ProjectWindowState()

    assert state.file_path is None
    assert state.get_file_name() is None
    assert state.get_status_file_text() == "Файл не открыт"


def test_project_window_state_with_file():
    state = ProjectWindowState(file_path="/tmp/project.json")

    assert state.get_file_name() == "project.json"
    assert state.get_status_file_text() == "Файл: project.json"
