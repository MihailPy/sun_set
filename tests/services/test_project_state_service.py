from sun_set.models.project_data import ProjectData
from sun_set.services.project_state_service import (
    build_export_action_tooltip,
    build_export_paths_text,
    build_export_paths_tooltip,
    build_project_data,
    can_export_images,
    can_preview_image,
    get_export_paths_from_project,
    get_project_settings,
    normalize_optional_path,
    restore_optional_path,
)


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


def test_normalize_optional_path():
    assert normalize_optional_path("") is None
    assert normalize_optional_path("/tmp/file.json") == "/tmp/file.json"


def test_restore_optional_path():
    assert restore_optional_path(None) == ""
    assert restore_optional_path("/tmp/export") == "/tmp/export"


def test_build_export_paths_text_without_paths():
    text = build_export_paths_text(
        export_settings_path="",
        export_output_dir="",
    )

    assert text == "Настройки: не выбраны | Папка: не выбрана"


def test_build_export_paths_text_with_paths():
    text = build_export_paths_text(
        export_settings_path="/tmp/export_settings.json",
        export_output_dir="/tmp/images",
    )

    assert text == "Настройки: export_settings.json | Папка: images"


def test_build_export_paths_tooltip_without_paths():
    tooltip = build_export_paths_tooltip(
        export_settings_path="",
        export_output_dir="",
    )

    assert tooltip == ""


def test_build_export_paths_tooltip_with_paths():
    tooltip = build_export_paths_tooltip(
        export_settings_path="/tmp/export_settings.json",
        export_output_dir="/tmp/images",
    )

    assert "Файл настроек: /tmp/export_settings.json" in tooltip
    assert "Папка экспорта: /tmp/images" in tooltip


def test_can_preview_image():
    assert can_preview_image(
        has_selected_cities=True,
        export_settings_path="/tmp/settings.json",
    )

    assert not can_preview_image(
        has_selected_cities=False,
        export_settings_path="/tmp/settings.json",
    )

    assert not can_preview_image(
        has_selected_cities=True,
        export_settings_path="",
    )


def test_can_export_images():
    assert can_export_images(
        has_selected_cities=True,
        export_settings_path="/tmp/settings.json",
        export_output_dir="/tmp/export",
    )

    assert not can_export_images(
        has_selected_cities=False,
        export_settings_path="/tmp/settings.json",
        export_output_dir="/tmp/export",
    )

    assert not can_export_images(
        has_selected_cities=True,
        export_settings_path="",
        export_output_dir="/tmp/export",
    )

    assert not can_export_images(
        has_selected_cities=True,
        export_settings_path="/tmp/settings.json",
        export_output_dir="",
    )


def test_build_export_action_tooltip():
    assert (
        build_export_action_tooltip(
            has_selected_cities=False,
            export_settings_path="/tmp/settings.json",
            export_output_dir="/tmp/export",
        )
        == "Выберите один или несколько городов в таблице"
    )

    assert (
        build_export_action_tooltip(
            has_selected_cities=True,
            export_settings_path="",
            export_output_dir="/tmp/export",
        )
        == "Выберите файл настроек экспорта"
    )

    assert (
        build_export_action_tooltip(
            has_selected_cities=True,
            export_settings_path="/tmp/settings.json",
            export_output_dir="",
        )
        == "Выберите папку экспорта"
    )

    assert (
        build_export_action_tooltip(
            has_selected_cities=True,
            export_settings_path="/tmp/settings.json",
            export_output_dir="/tmp/export",
        )
        == ""
    )


def test_get_export_paths_from_project():
    project = ProjectData(
        year=2027,
        weekday1=4,
        weekday2=5,
        cities=[],
        export_settings_path="/tmp/settings.json",
        export_output_dir="/tmp/export",
    )

    export_paths = get_export_paths_from_project(project)

    assert export_paths.settings_path == "/tmp/settings.json"
    assert export_paths.output_dir == "/tmp/export"


def test_get_export_paths_from_project_without_paths():
    project = ProjectData(
        year=2027,
        weekday1=4,
        weekday2=5,
        cities=[],
        export_settings_path=None,
        export_output_dir=None,
    )

    export_paths = get_export_paths_from_project(project)

    assert export_paths.settings_path == ""
    assert export_paths.output_dir == ""


def test_get_project_settings():
    project = ProjectData(
        year=2030,
        weekday1=1,
        weekday2=6,
        cities=[],
    )

    settings = get_project_settings(project)

    assert settings.year == 2030
    assert settings.weekday1 == 1
    assert settings.weekday2 == 6
