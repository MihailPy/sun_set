# связывает все вместе
import re
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from sun_set.image_export.errors import get_user_friendly_error
from sun_set.image_export.layout import (
    build_export_data_from_city,
    build_text_blocks,
)
from sun_set.image_export.renderer import render_image, render_image_to_pil
from sun_set.image_export.settings import ExportImageSettings, load_export_settings
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
                    error=get_user_friendly_error(error),
                )
            )

    return results


def build_city_image_preview(city, settings_path: Path) -> Image.Image:
    settings = load_export_settings(settings_path)
    export_data = build_export_data_from_city(city)
    text_blocks = build_text_blocks(export_data, settings.layout)

    return render_image_to_pil(
        settings=settings,
        text_blocks=text_blocks,
    )


def build_city_image_preview_from_settings(
    city,
    settings: ExportImageSettings,
) -> Image.Image:
    export_data = build_export_data_from_city(city)
    text_blocks = build_text_blocks(export_data, settings.layout)

    return render_image_to_pil(
        settings=settings,
        text_blocks=text_blocks,
    )


def build_export_report(results: list[ExportResult]) -> str:
    success_count = sum(result.success for result in results)
    error_count = len(results) - success_count

    report_lines = [
        f"Готово: {success_count}",
        f"Ошибки: {error_count}",
        "",
    ]

    for result in results:
        if result.success:
            report_lines.append(f"OK: {result.city_name} -> {result.output_path}")
        else:
            report_lines.append(f"ERROR: {result.city_name} -> {result.error}")

    return "\n".join(report_lines)


def build_export_summary_message(results: list[ExportResult]) -> str:
    success_count = sum(result.success for result in results)
    error_count = len(results) - success_count

    message = f"Готово: {success_count}\nОшибки: {error_count}"

    failed_results = [result for result in results if not result.success]

    if failed_results:
        errors_text = "\n".join(
            f"- {result.city_name}: {result.error}" for result in failed_results[:10]
        )

        message += f"\n\nОшибки:\n{errors_text}"

        if len(failed_results) > 10:
            message += f"\n...и ещё {len(failed_results) - 10}"

    return message
