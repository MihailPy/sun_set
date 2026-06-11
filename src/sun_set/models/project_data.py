from dataclasses import dataclass, field

from sun_set.constants.project_format import PROJECT_FORMAT_VERSION
from sun_set.models.city import City


@dataclass
class ProjectData:
    version: int = PROJECT_FORMAT_VERSION
    year: int = 2026
    weekday1: int = 4
    weekday2: int = 5
    cities: list[City] = field(default_factory=list)
    export_settings_path: str | None = None
    export_output_dir: str | None = None
