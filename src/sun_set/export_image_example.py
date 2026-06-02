from pathlib import Path

from sun_set.image_export.service import export_city_image
from sun_set.storage.city_json_storage import load_from_json


def main() -> None:
    cities_path = "cities.json"
    settings_path = Path("examples/image_export/default_white.json")
    output_path = Path("out/image_export_example.png")

    cities, _ = load_from_json(cities_path)

    if cities is None:
        print("Cities is None")
        return

    city = cities[0]

    export_city_image(
        city=city,
        settings_path=settings_path,
        output_path=output_path,
    )

    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    main()
