import json
import sys
from PyQt6.QtWidgets import QApplication
from sun_set.views.main_view import MainWindow

from sun_set.models.city import City
from sun_set.api.file_manager import load_from_json, save_to_json


def main():
    cities = load_from_json("cities.json")
    if isinstance(cities, str):
        print(f"{cities}")
        cities = []

    if isinstance(cities, list):  # type: ignore
        if not cities:
            city = City("Moscow", "Moscow", 55.7558, 37.6173, "Europe/Moscow", 156)
            cities.append(city)
            save_to_json(cities, "cities.json")
    print(json.dumps([city.__dict__ for city in cities], indent=4, ensure_ascii=False))

    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
