# dataclass-модели настроек


from dataclasses import dataclass


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
