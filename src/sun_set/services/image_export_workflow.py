from pathlib import Path

from PIL import Image

from sun_set.image_export.service import (
    ExportResult,
    build_city_image_preview,
    export_cities_images,
    save_export_report,
)
from sun_set.models.city import City


def export_selected_city_images(
    cities: list[City],
    settings_path: Path,
    output_dir: Path,
) -> list[ExportResult]:
    results = export_cities_images(
        cities=cities,
        settings_path=settings_path,
        output_dir=output_dir,
    )

    save_export_report(results, output_dir)

    return results


def build_selected_city_preview_image(
    city: City,
    settings_path: Path,
) -> Image.Image:
    return build_city_image_preview(
        city=city,
        settings_path=settings_path,
    )
