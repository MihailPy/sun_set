# связывает все вместе

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
