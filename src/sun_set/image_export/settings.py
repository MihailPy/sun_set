# dataclass-модели настроек

from dataclasses import asdict, dataclass
from json import JSONDecodeError
from pathlib import Path

from dacite import Config, DaciteError, from_dict

from sun_set.image_export.errors import ExportSettingsError
from sun_set.storage.json_storage import read_json, write_json


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
    try:
        data = read_json(path)

        if not isinstance(data, dict):
            raise ExportSettingsError(
                "Корневой элемент файла настроек должен быть объектом."
            )

        settings = from_dict(
            data_class=ExportImageSettings,
            data=data,
            config=Config(
                cast=[int],
                type_hooks={
                    dict[int, MonthBlockSettings]: lambda values: {
                        int(key): from_dict(MonthBlockSettings, value)
                        for key, value in values.items()
                    }
                },
            ),
        )

        validate_export_settings(settings)
        return settings

    except FileNotFoundError as error:
        raise ExportSettingsError("Файл настроек экспорта не найден.") from error

    except JSONDecodeError as error:
        raise ExportSettingsError(
            "Файл настроек экспорта не является корректным JSON."
        ) from error

    except DaciteError as error:
        raise ExportSettingsError(
            f"Некорректная структура настроек экспорта: {error}"
        ) from error

    except (TypeError, ValueError) as error:
        raise ExportSettingsError(
            f"Некорректные значения в настройках экспорта: {error}"
        ) from error


def save_export_settings(settings: ExportImageSettings, path: Path) -> None:
    validate_export_settings(settings)
    write_json(path, asdict(settings))


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


def create_default_export_settings() -> ExportImageSettings:
    return ExportImageSettings(
        image=ImageSettings(
            width=1000,
            height=1400,
            background_color="#ffffff",
            template_path=None,
        ),
        text=TextSettings(
            font_path=None,
            font_size=24,
            color="#000000",
        ),
        layout=LayoutSettings(
            row_height=32,
            first_column_offset_x=10,
            second_column_offset_x=130,
            month_blocks={
                month: MonthBlockSettings(
                    x=40 + ((month - 1) % 3) * 320,
                    y=60 + ((month - 1) // 3) * 320,
                )
                for month in range(1, 13)
            },
        ),
    )


def save_month_positions(
    month_blocks: dict[int, MonthBlockSettings],
    path: Path,
) -> None:
    missing_months = [month for month in range(1, 13) if month not in month_blocks]

    if missing_months:
        missing_text = ", ".join(str(month) for month in missing_months)
        raise ExportSettingsError(f"Missing month blocks: {missing_text}")

    unexpected_months = [month for month in month_blocks if month not in range(1, 13)]

    if unexpected_months:
        unexpected_text = ", ".join(str(month) for month in unexpected_months)
        raise ExportSettingsError(f"Unexpected month blocks: {unexpected_text}")

    data = {str(month): asdict(month_blocks[month]) for month in range(1, 13)}

    write_json(path, data)


def load_month_positions(
    path: Path,
) -> dict[int, MonthBlockSettings]:
    try:
        data = read_json(path)

        if not isinstance(data, dict):
            raise ExportSettingsError(
                "Корневой элемент файла координат должен быть объектом."
            )

        month_blocks = {
            int(month): from_dict(
                MonthBlockSettings,
                values,
            )
            for month, values in data.items()
        }

        missing_months = [month for month in range(1, 13) if month not in month_blocks]

        if missing_months:
            missing_text = ", ".join(str(month) for month in missing_months)
            raise ExportSettingsError(f"Missing month blocks: {missing_text}")

        return month_blocks

    except FileNotFoundError as error:
        raise ExportSettingsError("Файл координат месяцев не найден.") from error

    except JSONDecodeError as error:
        raise ExportSettingsError(
            "Файл координат месяцев не является корректным JSON."
        ) from error

    except DaciteError as error:
        raise ExportSettingsError(
            f"Некорректная структура координат месяцев: {error}"
        ) from error

    except (TypeError, ValueError) as error:
        raise ExportSettingsError(
            f"Некорректные значения координат месяцев: {error}"
        ) from error
