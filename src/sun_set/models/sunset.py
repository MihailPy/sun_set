from dataclasses import dataclass
from enum import Enum, auto


class AutoName(Enum):
    @staticmethod
    def _generate_next_value_(name, start, count, last_values):
        return name


class Source(Enum):
    CALCULATED = auto()
    EDITED = auto()
    ERROR_POLAR = auto()


@dataclass
class SunsetEntry:
    day: int
    weekday: int
    time: str
    source: Source


@dataclass
class MonthData:
    month: int
    days: list[SunsetEntry]  # noqa: F821


@dataclass
class YearData:
    year: int
    source: Source
    hash_before_edit: str | None
    months: list[MonthData] | None
