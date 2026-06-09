from dataclasses import dataclass

from sun_set.models.city import City


@dataclass
class ProjectData:
    year: int
    weekday1: int
    weekday2: int
    cities: list[City]
    export_settings_path: str | None = None
    export_output_dir: str | None = None
