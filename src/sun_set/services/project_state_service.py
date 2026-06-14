from pathlib import Path

from sun_set.models.city import City
from sun_set.models.project_data import ProjectData


def build_project_data(
    year: int,
    weekday1: int,
    weekday2: int,
    cities: list[City],
    export_settings_path: str,
    export_output_dir: str,
) -> ProjectData:
    return ProjectData(
        year=year,
        weekday1=weekday1,
        weekday2=weekday2,
        cities=cities,
        export_settings_path=normalize_optional_path(export_settings_path),
        export_output_dir=normalize_optional_path(export_output_dir),
    )


def normalize_optional_path(path: str) -> str | None:
    return path or None


def restore_optional_path(path: str | None) -> str:
    return path or ""


def build_export_paths_text(
    export_settings_path: str,
    export_output_dir: str,
) -> str:
    settings_text = "не выбраны"
    output_dir_text = "не выбрана"

    if export_settings_path:
        settings_text = Path(export_settings_path).name

    if export_output_dir:
        output_dir_text = Path(export_output_dir).name

    return f"Настройки: {settings_text} | Папка: {output_dir_text}"


def build_export_paths_tooltip(
    export_settings_path: str,
    export_output_dir: str,
) -> str:
    tooltip_parts = []

    if export_settings_path:
        tooltip_parts.append(f"Файл настроек: {export_settings_path}")

    if export_output_dir:
        tooltip_parts.append(f"Папка экспорта: {export_output_dir}")

    return "\n".join(tooltip_parts)


def can_preview_image(
    has_selected_cities: bool,
    export_settings_path: str,
) -> bool:
    return has_selected_cities and bool(export_settings_path)


def can_export_images(
    has_selected_cities: bool,
    export_settings_path: str,
    export_output_dir: str,
) -> bool:
    return (
        has_selected_cities and bool(export_settings_path) and bool(export_output_dir)
    )
