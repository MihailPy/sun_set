# dataclass-модели настроек

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from dacite import Config, from_dict

from sun_set.image_export.errors import ExportSettingsError


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
    first_column_offset_x: int
    second_column_offset_x: int
    month_blocks: dict[int, MonthBlockSettings]


@dataclass
class ExportImageSettings:
    image: ImageSettings
    text: TextSettings
    layout: LayoutSettings


def load_export_settings(path: Path) -> ExportImageSettings:
    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    settings = from_dict(
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
    validate_export_settings(settings)
    return settings


def save_export_settings(settings: ExportImageSettings, path: Path) -> None:
    validate_export_settings(settings)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            asdict(settings),
            file,
            ensure_ascii=False,
            indent=2,
        )


def validate_export_settings(settings: ExportImageSettings) -> None:
    if settings.image.width <= 0:
        raise ExportSettingsError("Image width must be greater than 0")

    if settings.image.height <= 0:
        raise ExportSettingsError("Image height must be greater than 0")

    if not settings.image.background_color:
        raise ExportSettingsError("Background color is required")

    if settings.text.font_size <= 0:
        raise ExportSettingsError("Font size must be greater than 0")

    if not settings.text.color:
        raise ExportSettingsError("Text color is required")

    if settings.layout.row_height <= 0:
        raise ExportSettingsError("Row height must be greater than 0")

    missing_months = [
        month for month in range(1, 13) if month not in settings.layout.month_blocks
    ]

    if missing_months:
        missing_months_text = ", ".join(str(month) for month in missing_months)

        raise ExportSettingsError(f"Missing month blocks: {missing_months_text}")
