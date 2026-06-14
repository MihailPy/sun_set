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
        export_settings_path=export_settings_path or None,
        export_output_dir=export_output_dir or None,
    )
