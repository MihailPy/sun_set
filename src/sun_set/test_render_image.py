from pathlib import Path

from sun_set.api.file_manager import load_from_json
from sun_set.image_export.service import export_city_image


def main():
    root_dir = Path(__file__).resolve().parent.parent.parent
    settings_path = root_dir / "settings.json"
    print(f"{settings_path=}")

    cities, error = load_from_json("cities.json")

    if cities is None:
        return

    output_path = root_dir / "image_output.png"
    export_city_image(cities[0], settings_path, output_path)


if __name__ == "__main__":
    main()
