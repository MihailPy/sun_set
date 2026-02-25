from dataclasses import dataclass

from sun_set.models.sunset import YearData


@dataclass
class City:
    name: str
    region: str
    lat: float
    lon: float
    timezone: str
    elevation: int
    sunset_data: YearData

    def __hash__(self) -> int:
        return hash((self.lat, self.lon, self.timezone, self.elevation))
