# dataclass-модели настроек

import json
from dataclasses import dataclass
from pathlib import Path

from dacite import Config, from_dict


@dataclass
class ImageSettings:
    width: int
    height: int
    background_color: str
    template_path: str | None


@dataclass
class TextSettings:
    font_path: str | None
    font_size: int
    color: str


@dataclass
class MonthBlockSettings:
    x: int
    y: int


@dataclass
class LayoutSettings:
    row_height: int
    meeting_offset_x: int
    sunset_offset_x: int
    month_blocks: dict[int, MonthBlockSettings]


@dataclass
class ExportImageSettings:
    image: ImageSettings
    text: TextSettings
    layout: LayoutSettings


def load_export_settings(path: Path) -> ExportImageSettings:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return from_dict(
        data_class=ExportImageSettings,
        data=data,
        config=Config(
            cast=[int],
            type_hooks={
                dict[int, MonthBlockSettings]: lambda d: {
                    int(k): from_dict(MonthBlockSettings, v) for k, v in d.items()
                }
            },
        ),
    )
