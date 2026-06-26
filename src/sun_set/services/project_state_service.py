from dataclasses import dataclass
from pathlib import Path

from sun_set.models.city import City
from sun_set.models.project_data import ProjectData


@dataclass(frozen=True)
class ProjectSettings:
    year: int
    weekday1: int
    weekday2: int


@dataclass(frozen=True)
class ExportPaths:
    settings_path: str
    output_dir: str


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


def build_export_paths_text(export_paths: ExportPaths) -> str:
    settings_text = "не выбраны"
    output_dir_text = "не выбрана"

    if export_paths.settings_path:
        settings_text = Path(export_paths.settings_path).name

    if export_paths.output_dir:
        output_dir_text = Path(export_paths.output_dir).name

    return f"Настройки: {settings_text} | Папка: {output_dir_text}"


def build_export_paths_tooltip(export_paths: ExportPaths) -> str:
    tooltip_parts = []

    if export_paths.settings_path:
        tooltip_parts.append(f"Файл настроек: {export_paths.settings_path}")

    if export_paths.output_dir:
        tooltip_parts.append(f"Папка экспорта: {export_paths.output_dir}")

    return "\n".join(tooltip_parts)


def can_preview_image(
    has_selected_cities: bool,
    export_paths: ExportPaths,
) -> bool:
    return has_selected_cities and bool(export_paths.settings_path)


def can_export_images(
    has_selected_cities: bool,
    export_paths: ExportPaths,
) -> bool:
    return (
        has_selected_cities
        and bool(export_paths.settings_path)
        and bool(export_paths.output_dir)
    )


def build_export_action_tooltip(
    has_selected_cities: bool,
    export_paths: ExportPaths,
) -> str:
    if not has_selected_cities:
        return "Выберите один или несколько городов в таблице"

    if not export_paths.settings_path:
        return "Выберите файл настроек экспорта"

    if not export_paths.output_dir:
        return "Выберите папку экспорта"

    return ""


def get_export_paths_from_project(project: ProjectData) -> ExportPaths:
    return ExportPaths(
        settings_path=restore_optional_path(project.export_settings_path),
        output_dir=restore_optional_path(project.export_output_dir),
    )


def get_project_settings(project: ProjectData) -> ProjectSettings:
    return ProjectSettings(
        year=project.year,
        weekday1=project.weekday1,
        weekday2=project.weekday2,
    )


def export_settings_path_exists(export_paths: ExportPaths) -> bool:
    return (
        bool(export_paths.settings_path) and Path(export_paths.settings_path).exists()
    )


def export_output_dir_exists(export_paths: ExportPaths) -> bool:
    return bool(export_paths.output_dir) and Path(export_paths.output_dir).exists()


@dataclass
class ExportPathState:
    paths: ExportPaths

    @classmethod
    def empty(cls) -> "ExportPathState":
        return cls(
            paths=ExportPaths(
                settings_path="",
                output_dir="",
            )
        )

    def set_settings_path(self, settings_path: str) -> None:
        self.paths = ExportPaths(
            settings_path=settings_path,
            output_dir=self.paths.output_dir,
        )

    def set_output_dir(self, output_dir: str) -> None:
        self.paths = ExportPaths(
            settings_path=self.paths.settings_path,
            output_dir=output_dir,
        )

    def clear_settings_path(self) -> None:
        self.set_settings_path("")

    def clear_output_dir(self) -> None:
        self.set_output_dir("")

    def set_paths(self, paths: ExportPaths) -> None:
        self.paths = paths
