import copy

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QApplication, QLineEdit, QTableWidget

from sun_set.core.astronomy import get_city_sunset
from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData
from sun_set.views.sunset_table_view import YearEditorWindow


@pytest.fixture(scope="session")
def qapp():
    """Фикстура, создающая QApplication для всего сеанса тестирования."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def city_with_data():
    """Создает City с тестовыми данными на 2024 год."""

    sunset_data = YearData(
        year=2024, source=Source.CALCULATED, hash_before_edit=None, months=None
    )

    city = City(
        name="Test City",
        region="Test Region",
        lat=55.7558,
        lon=37.6173,
        timezone="Europe/Moscow",
        elevation=170,
        sunset_data=sunset_data,
    )

    city.sunset_data = get_city_sunset(city, 2024, 0, 1)

    return city


@pytest.fixture
def city_not_enough_data(city_with_data):
    """Создает фикстуру с months меньше 12, остальные данные полная копия city_with_data."""
    new_city = copy.deepcopy(city_with_data)
    new_city.sunset_data.months = new_city.sunset_data.months[:3]
    return new_city


@pytest.fixture
def city_without_data():
    """Создает City без данных о закатах."""
    sunset_data = YearData(
        year=2024, source=Source.CALCULATED, hash_before_edit="test_hash", months=None
    )

    city = City(
        name="Empty City",
        region="Test Region",
        lat=55.7558,
        lon=37.6173,
        timezone="Europe/Moscow",
        elevation=170,
        sunset_data=sunset_data,
    )

    return city


def test_year_editor_window_initialization(qapp, city_with_data):
    """
    Тест проверяет, что окно создается корректно:
    - Заголовок содержит название города и год.
    - Количество вкладок соответствует количеству месяцев.
    """
    from sun_set.views.sunset_table_view import YearEditorWindow

    window = YearEditorWindow(city_with_data)

    # Проверка заголовка
    expected_title = (
        f"Данные города {city_with_data.name} за {city_with_data.sunset_data.year} год"
    )
    assert window.windowTitle() == expected_title

    # Проверка количества вкладок
    assert window.tabs.count() == len(city_with_data.sunset_data.months)

    # Очистка после теста
    window.close()


def test_year_editor_window_no_data(qapp, city_without_data):
    """
    Тест проверяет, что при отсутствии данных выбрасывается ValuerError.
    """
    with pytest.raises(ValueError, match="Нет данных о закатах для отображения"):
        YearEditorWindow(city_without_data)


def test_year_editor_window_not_enough_data(qapp, city_not_enough_data):
    """
    Тест проверяет, если в months кол-во элементов меньше 12, выбрасывается ValueError
    """
    with pytest.raises(ValueError, match="В months, элементов меньше 12"):
        YearEditorWindow(city_not_enough_data)


def test_year_editor_window_table_rows(qapp, city_with_data):
    """
    Проверяет, что для каждого месяца создается таблица с правильным количеством строк.
    """
    window = YearEditorWindow(city_with_data)

    # Проверяем каждую вкладку
    for tab_index in range(window.tabs.count()):
        # Получаем виджет вкладки
        tab_widget = window.tabs.widget(tab_index)
        if tab_widget is None:
            raise RuntimeError("Вкладка не найдена")
        # Находим QTableWidget внутри вкладки
        table = tab_widget.findChild(QTableWidget)  # noqa: F821
        assert table is not None, f"Table not found in tab {tab_index}"

        # Получаем данные месяца для этой вкладки
        month_data = city_with_data.sunset_data.months[tab_index]

        # Проверяем количество строк
        assert table.rowCount() == len(month_data.days), (
            f"Month {month_data.month}: expected {len(month_data.days)} rows, got {table.rowCount()}"
        )

    window.close()


def test_year_editor_window_edit_time(qapp, city_with_data):
    """Проверяет, что редактирование времени обновляет данные и сигналы."""
    window = YearEditorWindow(city_with_data)

    # Подключаемся к сигналу для проверки
    signal_received = []
    window.dataChanged.connect(lambda: signal_received.append(True))

    # Получаем таблицу первой вкладки (январь)
    tab_widget = window.tabs.widget(0)
    if tab_widget is None:
        raise RuntimeError("Первая вкладка не найдена")
    table = tab_widget.findChild(QTableWidget)

    # Сохраняем исходные данные
    original_time = city_with_data.sunset_data.months[0].days[0].time
    original_source = city_with_data.sunset_data.months[0].days[0].source

    # Эмулируем редактирование
    item = table.item(0, 2)
    if item:
        table.editItem(item)

        editor = table.findChild(QLineEdit)

        if editor:
            editor.clear()
            # Печатаем текст прямо в QLineEdit
            QTest.keyClicks(editor, "17:20")  # type: ignore
            # Подтверждаем ввод нажатием Enter
            QTest.keyClick(editor, Qt.Key.Key_Tab)  # type: ignore

        else:
            raise RuntimeError("Редактор не найден")

    # Проверяем результат
    new_time = city_with_data.sunset_data.months[0].days[0].time
    new_source = city_with_data.sunset_data.months[0].days[0].source

    assert len(signal_received) > 0, "Сигнал не был получен"
    assert original_time != new_time
    assert original_source is not new_source
    assert city_with_data.sunset_data.source is Source.EDITED

    window.close()
