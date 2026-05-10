from dataclasses import dataclass

from sun_set.image_export.layout import (
    build_export_data_from_city,
    build_text_blocks_for_month,
)
from sun_set.image_export.settings import LayoutSettings, MonthBlockSettings


def test_build_text_blocks_for_month():
    layout = LayoutSettings(
        row_height=30,
        meeting_offset_x=10,
        sunset_offset_x=100,
        month_blocks={
            1: MonthBlockSettings(x=40, y=200),
        },
    )

    blocks = build_text_blocks_for_month(
        month=1,
        rows=[
            ("17:10", "17:45"),
            ("17:20", "17:55"),
        ],
        layout=layout,
    )

    assert len(blocks) == 4

    assert blocks[0].text == "17:10"
    assert blocks[0].x == 50
    assert blocks[0].y == 200

    assert blocks[1].text == "17:45"
    assert blocks[1].x == 140
    assert blocks[1].y == 200

    assert blocks[2].text == "17:20"
    assert blocks[2].x == 50
    assert blocks[2].y == 230

    assert blocks[3].text == "17:55"
    assert blocks[3].x == 140
    assert blocks[3].y == 230


@dataclass
class Day:
    day: int
    weekday: int
    time: str


@dataclass
class Month:
    month: int
    days: list[Day]


@dataclass
class SunsetData:
    year: int
    months: list[Month] | None


@dataclass
class City:
    name: str
    sunset_data: SunsetData


def test_empty_city_data():
    city = City(name="Test", sunset_data=SunsetData(year=2023, months=[]))
    result = build_export_data_from_city(city)  # type: ignore[reportArgumentType]

    assert result.city_name == "Test"
    assert result.months == []


def test_paired_days_logic():
    # Дни 1 и 2 идут подряд — должны попасть в одну Row
    days = [Day(day=1, weekday=0, time="18:00"), Day(day=2, weekday=1, time="18:05")]
    month = Month(month=1, days=days)
    city = City(name="Test", sunset_data=SunsetData(year=2023, months=[month]))

    result = build_export_data_from_city(city)  # type: ignore[reportArgumentType]

    rows = result.months[0].rows
    assert len(rows) == 1
    assert rows[0].first_day_sunset is not None
    assert rows[0].first_day_sunset.day == "1"
    assert rows[0].second_day_sunset is not None
    assert rows[0].second_day_sunset.day == "2"


def test_single_day_distribution():
    days = [
        Day(day=1, weekday=0, time="18:00"),
        Day(day=3, weekday=2, time="18:10"),
    ]
    month = Month(month=1, days=days)
    city = City(name="Test", sunset_data=SunsetData(year=2023, months=[month]))

    result = build_export_data_from_city(city)  # type: ignore[reportArgumentType]
    rows = result.months[0].rows

    assert len(rows) in [1, 2]

    assert rows[0].first_day_sunset is not None
    assert rows[0].second_day_sunset is None

    if len(rows) == 2:
        assert rows[1].first_day_sunset is None
        assert rows[1].second_day_sunset is not None


def test_multiple_months():
    month1 = Month(month=1, days=[Day(day=1, weekday=0, time="17:00")])
    month2 = Month(month=2, days=[Day(day=1, weekday=1, time="18:00")])
    city = City(name="Test", sunset_data=SunsetData(year=2023, months=[month1, month2]))

    result = build_export_data_from_city(city)  # type: ignore[reportArgumentType]

    assert len(result.months) == 2
    assert result.months[0].month == 1
    assert result.months[1].month == 2
