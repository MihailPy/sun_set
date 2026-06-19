from pathlib import Path

from sun_set.image_export.service import (
    ExportResult,
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
