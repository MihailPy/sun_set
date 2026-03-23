import calendar
import datetime

import pytest

from sun_set.core.astronomy import get_city_sunset
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
        pytest.param(4, 3),
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
    call_count = 0
    year = 2024
    weekday1, weekday2 = 0, 1  # Понедельник и вторник

    # Вычисляем ожидаемое количество вызовов
    expected_calls = 0
    for month in range(1, 13):
        _, last_day = calendar.monthrange(year, month)
        for day in range(1, last_day + 1):
            current_date = datetime.date(year, month, day)
            if current_date.weekday() in {weekday1, weekday2}:
                expected_calls += 1

    # 2.1 Определяем функцию-заглушку (mock), которая всегда падает
    def mock_sunset(*args, **kwargs):
        """Заглушка, имитирующая ошибку библиотеки astral."""
        nonlocal call_count
        call_count += 1
        date_val = kwargs.get("date")

        if date_val and date_val.month == 6:
            raise ValueError("Солнце не садится (полярный день)")

        return datetime.time(18, 0)

    # 2.2 Подменяем настоящую функцию sunset на нашу заглушку
    monkeypatch.setattr("sun_set.core.astronomy.sunset", mock_sunset)

    # 2.3 Вызываем тестируемую функцию с данными для июня (например, year=2024, weekday1=0, weekday2=1)
    result = get_city_sunset(polar_city, year, weekday1, weekday2)

    # Проверяем структуру
    assert isinstance(result, YearData), "Result should be YearData"
    assert result.months is not None, "Months should not be None"
    assert result.source is Source.ERROR_POLAR

    # Проверяем, что июнь присутствует и все его дни имеют статус ошибки
    june_data = None
    for month_data in result.months:
        if month_data.month == 6:
            june_data = month_data
            break

    assert june_data is not None, "June should be present in result"
    assert len(june_data.days) > 0, "June should have at least one selected weekday"

    # Проверяем каждый день в июне
    for day_entry in june_data.days:
        assert day_entry.source == Source.ERROR_POLAR, (
            f"Day {day_entry.day} in June should have ERROR_POLAR status"
        )
        assert day_entry.time == "00:00", (
            f"Day {day_entry.day} in June should have time 00:00"
        )

    # Проверяем, что функция была вызвана для ВСЕХ выбранных дней недели
    assert call_count == expected_calls, (
        f"Expected {expected_calls} sunset calls, got {call_count}"
    )


@pytest.mark.parametrize("invalid_weekday", [-1, 7, 42, -100])
def test_get_city_sunset_invalid_weekday_range(normal_city, invalid_weekday):
    """
    Проверяем, что функция выбрасывает ValueError при передаче дня недели вне диапазона 0-6.
    """
    year = 2024
    with pytest.raises(ValueError):
        get_city_sunset(normal_city, year, invalid_weekday, invalid_weekday)


@pytest.mark.parametrize(
    "weekday1,weekday2",
    [
        (0, -1),
        (7, 1),
        (42, 42),
        (0, 7),
    ],
)
def test_get_city_sunset_invalid_weekday_combination(normal_city, weekday1, weekday2):
    """
    Проверяем, что функция падает, если хотя бы один из дней недели невалиден.
    """
    year = 2024
    with pytest.raises(ValueError):
        get_city_sunset(normal_city, year, weekday1, weekday2)
    pass


@pytest.mark.parametrize("weekday", [0, 1, 2, 3, 4, 5, 6])
def test_get_city_sunset_duplicate_weekdays(normal_city, weekday):
    """
    Проверяем, что при weekday1 == weekday2 функция работает корректно
    и возвращает YearData с пустым months.
    """
    year = 2024
    with pytest.raises(ValueError):
        get_city_sunset(normal_city, year, weekday, weekday)
