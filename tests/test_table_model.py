import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData
from sun_set.models.table_model import (
    CheckBoxHeader,
    CityTableModel,
    StatusActionDelegate,
)


@pytest.fixture
def qapp():
    """Создает QApplication для тестов"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def sample_city():
    """Создает City с тестовыми данными, фикстура"""
    city = City(
        name="Москва",
        region="Московская область",
        lat=55.7558,
        lon=37.6173,
        timezone="Europe/Moscow",
        elevation=156,
        sunset_data=YearData(
            year=2033, source=Source.CALCULATED, hash_before_edit=None, months=None
        ),
    )
    return city


@pytest.fixture
def sample_cities(sample_city):
    """Создает список тестовых городов"""
    city2 = City(
        name="Санкт-Петербург",
        region="Ленинградская область",
        lat=59.9343,
        lon=30.3351,
        timezone="Europe/Moscow",
        elevation=3,
        sunset_data=YearData(
            year=2033, source=Source.CALCULATED, hash_before_edit=None, months=None
        ),
    )
    return [sample_city, city2]


@pytest.fixture
def table_model(sample_cities, qapp):
    """Создает модель таблицы"""
    return CityTableModel(sample_cities)


@pytest.fixture
def status_delegate(qapp):
    """Создает делегат статуса"""
    return StatusActionDelegate()


@pytest.fixture
def checkbox_header(qapp):
    header = CheckBoxHeader(Qt.Orientation.Horizontal)
    header.setModel(CityTableModel([]))
    return header
