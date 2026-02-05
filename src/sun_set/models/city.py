from dataclasses import dataclass


@dataclass
class City:
    name: str
    region: str
    lat: float
    lon: float
    timezone: str
    elevation: int
