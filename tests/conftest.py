# tests/image_export/conftest.py

import copy
import json
from pathlib import Path

import pytest
from PIL import Image

from sun_set.core.astronomy import get_city_sunset
from sun_set.image_export.layout import TextBlock
from sun_set.image_export.settings import (
    ExportImageSettings,
    ImageSettings,
    LayoutSettings,
    MonthBlockSettings,
    TextSettings,
)
from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData


@pytest.fixture
def valid_settings_dict() -> dict:
    return {
        "image": {
            "width": 400,
            "height": 300,
            "background_color": "#ffffff",
            "template_path": None,
        },
        "text": {
            "font_path": None,
            "font_size": 20,
            "color": "#000000",
        },
        "layout": {
            "row_height": 30,
            "first_column_offset_x": 10,
            "second_column_offset_x": 120,
            "month_blocks": {
                str(month): {
                    "x": 40 + ((month - 1) % 3) * 120,
                    "y": 50 + ((month - 1) // 3) * 60,
                }
                for month in range(1, 13)
            },
        },
    }


@pytest.fixture
def settings_path(tmp_path: Path, valid_settings_dict: dict) -> Path:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(valid_settings_dict),
        encoding="utf-8",
    )
    return path


@pytest.fixture
def export_settings() -> ExportImageSettings:
    return ExportImageSettings(
        image=ImageSettings(
            width=400,
            height=300,
            background_color="#ffffff",
            template_path=None,
        ),
        text=TextSettings(
            font_path=None,
            font_size=20,
            color="#000000",
        ),
        layout=LayoutSettings(
            row_height=30,
            first_column_offset_x=10,
            second_column_offset_x=120,
            month_blocks={
                month: MonthBlockSettings(
                    x=40 + ((month - 1) % 3) * 120,
                    y=50 + ((month - 1) // 3) * 60,
                )
                for month in range(1, 13)
            },
        ),
    )


@pytest.fixture
def text_blocks() -> list[TextBlock]:
    return [
        TextBlock(text="17:10", x=50, y=50),
        TextBlock(text="17:45", x=150, y=50),
    ]


@pytest.fixture
def template_image_path(tmp_path: Path) -> Path:
    path = tmp_path / "template.png"
    image = Image.new("RGB", (50, 50), "#0000FF")
    image.save(path)
    return path


@pytest.fixture
def test_city() -> City:
    sunset_data = YearData(
        year=2024,
        source=Source.CALCULATED,
        hash_before_edit=None,
        months=None,
    )

    city = City(
        name="Test City",
        region="Test Region",
        lat=55.7558,
        lon=37.6173,
        timezone="Europe/Moscow",
        elevation=170,
        sunset_data=sunset_data,
    )

    city.sunset_data = get_city_sunset(city, 2024, 0, 1)

    if city.sunset_data.months is not None:
        city.sunset_data.months = city.sunset_data.months[:3]

    return city


@pytest.fixture
def second_test_city(test_city: City) -> City:
    city = copy.deepcopy(test_city)
    city.name = "Test City Two"
    return city
