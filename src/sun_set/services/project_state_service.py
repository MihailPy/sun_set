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
