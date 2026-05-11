from pathlib import Path

from sun_set.api.file_manager import load_from_json
from sun_set.image_export.layout import (
    build_export_data_from_city,
    build_text_blocks_for_month,
)
from sun_set.image_export.renderer import render_image
from sun_set.image_export.settings import load_export_settings


def main():
    root_dir = Path(__file__).resolve().parent.parent.parent
    settings_path = root_dir / "settings.json"
    print(f"{settings_path=}")

    settings = load_export_settings(settings_path)
    print(f"{settings=}")
    cities, error = load_from_json("cities.json")

    if cities is None:
        return

    export_data_from_city = build_export_data_from_city(cities[0])
    text_block = build_text_blocks_for_month(
        export_data_from_city.months[0], settings.layout
    )
    render_image(settings, text_block, root_dir / "image_output.png")


if __name__ == "__main__":
    main()
