import pytest

from sun_set.core.astronmy import get_city_sunset
from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData


# 1. Сначала создадим фикстуру для города за полярным кругом
@pytest.fixture
def polar_city():
    """Фикстура, возвращающая объект City для Мурманска."""
    # lat = 68.9, lon = 33.1, elevation = 50, timezone = 'Europe/Moscow'
    city = City(
        name="Polar city",
        region="Russia",
        lat=68.9,
        lon=33.1,
        timezone="Europe/Moscow",
        elevation=50,
        sunset_data=YearData(
            year=2024, source=Source.CALCULATED, hash_before_edit=None, months=None
        ),
    )
    return city


# 2. Теперь сам тест
def test_get_city_sunset_polar_day(polar_city, monkeypatch):
    """
    Тест проверяет, что функция выбрасывает исключение AstralError
    для города за полярным кругом в июне.
    """

    # 2.1 Определяем функцию-заглушку (mock), которая всегда падает
    def mock_sunset(*args, **kwargs):
        """Заглушка, имитирующая ошибку библиотеки astral."""
        raise ValueError("Солнце не садится (полярный день)")

    # 2.2 Подменяем настоящую функцию sunset на нашу заглушку
    monkeypatch.setattr("astral.sun.sunset", mock_sunset)

    # 2.3 Вызываем тестируемую функцию с данными для июня (например, year=2024, month=6)
    year = 2024
    weekday1 = 0  # Понедельник
    weekday2 = 1  # Вторник

    with pytest.raises(ValueError):
        get_city_sunset(polar_city, year, weekday1, weekday2)
