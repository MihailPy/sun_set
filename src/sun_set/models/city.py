import hashlib
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

    def get_stable_hash(self) -> str:
        """Детерминированный хеш для сохранения между запусками"""
        params = f"{self.lat}_{self.lon}_{self.timezone}_{self.elevation}"
        return hashlib.sha256(params.encode()).hexdigest()
