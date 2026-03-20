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


@pytest.fixture
def normal_city():
    """Фикстура, возвращающая объект City для Москвы."""
    # lat = 55.7558, lon = 37.6173, elevation = 170, timezone = 'Europe/Moscow'
    city = City(
        name="Moscow",
        region="Russia",
        lat=55.7558,
        lon=37.6173,
        timezone="Europe/Moscow",
        elevation=170,
        sunset_data=YearData(
            year=2024, source=Source.CALCULATED, hash_before_edit=None, months=None
        ),
    )
    return city


@pytest.mark.parametrize(
    "weekday1,weekday2",
    [
        pytest.param(0, 1),
        pytest.param(1, 2),
        pytest.param(6, 2),
        pytest.param(4, 5),
        pytest.param(4, 4),
    ],
)
def test_get_city_sunset_normal_city(normal_city, weekday1, weekday2):
    """
    Тест проверяет что при нормальных данных функция выдает
    объект YearData, с нужными данными.
    """
    year = 2024

    result = get_city_sunset(normal_city, year, weekday1, weekday2)

    assert type(result) is YearData
    assert result.year is year
    assert result.hash_before_edit is not None
    assert result.months is not None
    assert len(result.months) == 12
    assert result.months[0].days[0].weekday in {weekday1, weekday2}
    assert result.months[0].days[1].weekday in {weekday1, weekday2}
    assert result.months[3].days[2].weekday in {weekday1, weekday2}
    assert result.months[8].days[3].weekday in {weekday1, weekday2}


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
