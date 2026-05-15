# связывает все вместе
import re
from dataclasses import dataclass
from pathlib import Path

from sun_set.image_export.layout import (
    build_export_data_from_city,
    build_text_blocks,
)
from sun_set.image_export.renderer import render_image
from sun_set.image_export.settings import load_export_settings
from sun_set.models.city import City


def export_city_image(city: City, settings_path: Path, output_path: Path) -> None:
    settings = load_export_settings(settings_path)
    export_data = build_export_data_from_city(city)
    text_blocks = build_text_blocks(export_data, settings.layout)
    render_image(settings=settings, text_blocks=text_blocks, output_path=output_path)


@dataclass
class ExportResult:
    city_name: str
    output_path: Path | None
    success: bool
    error: str | None


def build_output_filename(city_name: str, year: int) -> str:
    safe_city_name = re.sub(r"[^\w\-]+", "_", city_name).strip("_")
    return f"{year}_{safe_city_name}.png"


def export_cities_images(
    cities: list,
    settings_path: Path,
    output_dir: Path,
) -> list[ExportResult]:
    output_dir.mkdir(parents=True, exist_ok=True)

    settings = load_export_settings(settings_path)
    results: list[ExportResult] = []

    for city in cities:
        output_path = output_dir / build_output_filename(
            city_name=city.name,
            year=city.sunset_data.year,
        )

        try:
            export_data = build_export_data_from_city(city)
            text_blocks = build_text_blocks(export_data, settings.layout)
            render_image(
                settings=settings,
                text_blocks=text_blocks,
                output_path=output_path,
            )

            results.append(
                ExportResult(
                    city_name=city.name,
                    output_path=output_path,
                    success=True,
                    error=None,
                )
            )
        except Exception as error:
            results.append(
                ExportResult(
                    city_name=city.name,
                    output_path=None,
                    success=False,
                    error=str(error),
                )
            )

    return results
