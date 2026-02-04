import json
from src.city import City, load_from_json, save_to_json


def main():
    print("Hello from sun-set!")
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


if __name__ == "__main__":
    main()
