import pytest

from sun_set.models.city import City


class TestCity:
    """Тесты для датакласса City"""

    def test_city_creation_with_valid_data(self):
        """Тест создания объекта City с корректными данными"""
        city = City(
            name="Москва",
            region="Московская область",
            lat=55.7558,
            lon=37.6176,
            timezone="Europe/Moscow",
            elevation=156,
        )

        assert city.name == "Москва"
        assert city.region == "Московская область"
        assert city.lat == 55.7558
        assert city.lon == 37.6176
        assert city.timezone == "Europe/Moscow"
        assert city.elevation == 156

    def test_city_creation_with_negative_coordinates(self):
        """Тест создания объекта с отрицательными координатами"""
        city = City(
            name="Буэнос-Айрес",
            region="Буэнос-Айрес",
            lat=-34.6037,
            lon=-58.3816,
            timezone="America/Argentina/Buenos_Aires",
            elevation=25,
        )

        assert city.lat == -34.6037
        assert city.lon == -58.3816

    def test_city_creation_with_zero_elevation(self):
        """Тест создания города с нулевой высотой над уровнем моря"""
        city = City(
            name="Амстердам",
            region="Северная Голландия",
            lat=52.3676,
            lon=4.9041,
            timezone="Europe/Amsterdam",
            elevation=0,
        )

        assert city.elevation == 0

    def test_city_equality(self):
        """Тест сравнения двух одинаковых городов"""
        city1 = City(
            "Москва", "Московская область", 55.7558, 37.6176, "Europe/Moscow", 156
        )
        city2 = City(
            "Москва", "Московская область", 55.7558, 37.6176, "Europe/Moscow", 156
        )

        assert city1 == city2

    def test_city_inequality(self):
        """Тест сравнения разных городов"""
        city1 = City(
            "Москва", "Московская область", 55.7558, 37.6176, "Europe/Moscow", 156
        )
        city2 = City(
            "Санкт-Петербург",
            "Ленинградская область",
            59.9311,
            30.3609,
            "Europe/Moscow",
            5,
        )

        assert city1 != city2

    def test_city_string_representation(self):
        """Тест строкового представления города"""
        city = City(
            name="Казань",
            region="Татарстан",
            lat=55.8304,
            lon=49.0661,
            timezone="Europe/Moscow",
            elevation=60,
        )

        expected_repr = "City(name='Казань', region='Татарстан', lat=55.8304, lon=49.0661, timezone='Europe/Moscow', elevation=60)"
        assert repr(city) == expected_repr

    def test_city_with_empty_strings(self):
        """Тест создания города с пустыми строковыми полями"""
        city = City(name="", region="", lat=0.0, lon=0.0, timezone="", elevation=0)

        assert city.name == ""
        assert city.region == ""
        assert city.timezone == ""

    def test_city_mutability(self):
        """Тест мутабельности датакласса (по умолчанию датаклассы изменяемы)"""
        city = City(
            name="Новосибирск",
            region="Новосибирская область",
            lat=55.0084,
            lon=82.9357,
            timezone="Asia/Novosibirsk",
            elevation=150,
        )

        # Изменяем атрибут
        city.name = "Красноярск"
        assert city.name == "Красноярск"

        # Изменяем другой атрибут
        city.elevation = 200
        assert city.elevation == 200

    def test_city_with_floats_precision(self):
        """Тест создания города с координатами с плавающей точкой"""
        city = City(
            name="Тестовый",
            region="Тестовая область",
            lat=55.123456789,
            lon=37.987654321,
            timezone="UTC",
            elevation=100,
        )

        assert isinstance(city.lat, float)
        assert isinstance(city.lon, float)
        assert city.lat == 55.123456789
        assert city.lon == 37.987654321


@pytest.mark.parametrize(
    "name, region, lat, lon, timezone, elevation",
    [
        ("Лондон", "Англия", 51.5074, -0.1278, "Europe/London", 11),
        ("Токио", "Канто", 35.6762, 139.6503, "Asia/Tokyo", 40),
        ("Сидней", "Новый Южный Уэльс", -33.8688, 151.2093, "Australia/Sydney", 58),
    ],
)
def test_city_parametrized(name, region, lat, lon, timezone, elevation):
    """Параметризованный тест создания городов"""
    city = City(name, region, lat, lon, timezone, elevation)

    assert city.name == name
    assert city.region == region
    assert city.lat == lat
    assert city.lon == lon
    assert city.timezone == timezone
    assert city.elevation == elevation


def test_city_as_dict():
    """Тест преобразования города в словарь"""
    city = City(
        name="Париж",
        region="Иль-де-Франс",
        lat=48.8566,
        lon=2.3522,
        timezone="Europe/Paris",
        elevation=35,
    )

    city_dict = {
        "name": "Париж",
        "region": "Иль-де-Франс",
        "lat": 48.8566,
        "lon": 2.3522,
        "timezone": "Europe/Paris",
        "elevation": 35,
    }

    assert city.__dict__ == city_dict


def test_city_with_invalid_types():
    """Тест: датакласс НЕ проверяет типы автоматически"""
    # Python с динамической типизацией, поэтому датакласс примет любые типы
    city = City(
        name=123,  # Должно быть str, но примет int
        region=["region"],  # Должно быть str, но примет list
        lat="55.7558",  # Должно быть float, но примет str
        lon=None,  # Должно быть float, но примет None
        timezone={},  # Должно быть str, но примет dict
        elevation="156",  # Должно быть int, но примет str
    )

    # Проверяем, что значения сохранились как есть, без преобразования типов
    assert city.name == 123
    assert city.region == ["region"]
    assert city.lat == "55.7558"
    assert city.lon is None
    assert city.timezone == {}
    assert city.elevation == "156"

    # Важно: это не вызовет ошибку, потому что датаклассы не валидируют типы!


def test_city_with_partial_data():
    """Тест создания города с частичными данными (все поля обязательны)"""
    # Датакласс требует все поля, это вызовет ошибку
    with pytest.raises(TypeError):
        City(name="Москва")  # Не хватает обязательных параметров


@pytest.fixture
def moscow_city():
    """Фикстура с данными Москвы"""
    return City(
        name="Москва",
        region="Московская область",
        lat=55.7558,
        lon=37.6176,
        timezone="Europe/Moscow",
        elevation=156,
    )


@pytest.fixture
def spb_city():
    """Фикстура с данными Санкт-Петербурга"""
    return City(
        name="Санкт-Петербург",
        region="Ленинградская область",
        lat=59.9311,
        lon=30.3609,
        timezone="Europe/Moscow",
        elevation=5,
    )


def test_with_fixtures(moscow_city, spb_city):
    """Пример использования фикстур"""
    assert moscow_city.name == "Москва"
    assert spb_city.name == "Санкт-Петербург"
    assert moscow_city != spb_city


def test_city_copy_and_modify(moscow_city):
    """Тест копирования и модификации города"""
    from copy import deepcopy

    # Создаем копию
    moscow_copy = deepcopy(moscow_city)
    assert moscow_copy == moscow_city

    # Модифицируем копию
    moscow_copy.name = "Москва (копия)"
    moscow_copy.elevation = 200

    assert moscow_copy != moscow_city
    assert moscow_city.name == "Москва"
    assert moscow_copy.name == "Москва (копия)"
