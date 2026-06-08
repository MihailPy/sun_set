from dataclasses import dataclass

from sun_set.models.city import City


@dataclass
class ProjectData:
    year: int
    weekday1: int
    weekday2: int
    cities: list[City]
