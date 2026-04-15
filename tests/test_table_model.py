import pytest
from PyQt6.QtCore import QModelIndex, Qt
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
    return City(
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


class TestCityTableModel:
    def test_row_count(self, table_model, sample_cities):
        """Тест количества строк"""
        assert table_model.rowCount() == len(sample_cities)

    def test_column_count(self, table_model):
        """Тест количества колонок"""
        assert table_model.columnCount() == 8

    def test_flags(self, table_model):
        """Тест флагов для разных колонок"""
        # Колонка с чекбоксом
        index = table_model.index(0, 0)
        flags = table_model.flags(index)
        assert flags & Qt.ItemFlag.ItemIsUserCheckable

        # Колонка с кнопками
        index = table_model.index(0, 7)
        flags = table_model.flags(index)
        assert flags & Qt.ItemFlag.ItemIsEnabled

        # Обычная колонка
        index = table_model.index(0, 1)
        flags = table_model.flags(index)
        assert flags & Qt.ItemFlag.ItemIsEditable

    def test_data_display_role(self, table_model, sample_city):
        """Тест получения данных для отображения"""
        index = table_model.index(0, 1)
        assert table_model.data(index, Qt.ItemDataRole.DisplayRole) == sample_city.name

        index = table_model.index(0, 2)
        assert (
            table_model.data(index, Qt.ItemDataRole.DisplayRole) == sample_city.region
        )

        index = table_model.index(0, 3)
        assert table_model.data(index, Qt.ItemDataRole.DisplayRole) == str(
            sample_city.lat
        )

    def test_data_check_state_role(self, table_model):
        """Тест состояния чекбокса"""
        index = table_model.index(0, 0)

        state = table_model.data(index, Qt.ItemDataRole.CheckStateRole)
        assert state == Qt.CheckState.Unchecked

        table_model.checked_states[0] = True
        state = table_model.data(index, Qt.ItemDataRole.CheckStateRole)
        assert state == Qt.CheckState.Checked

    def test_data_status_column(self, table_model, sample_city):
        """Тест данных в колонке статуса"""
        index = table_model.index(0, 7)

        status = table_model.data(index, Qt.ItemDataRole.DisplayRole)
        assert status == "❗️ Неактуальные данные"

        sample_city.sunset_data.hash_before_edit = sample_city.get_stable_hash()
        sample_city.sunset_data.source = Source.CALCULATED
        status = table_model.data(index, Qt.ItemDataRole.DisplayRole)
        assert status == "✅ Загружено"

    def test_data_view_enabled_role(self, table_model, sample_city):
        """Тест роли включения кнопки просмотра"""
        index = table_model.index(0, 7)

        sample_city.sunset_data.hash_before_edit = sample_city.get_stable_hash()
        enabled = table_model.data(index, StatusActionDelegate.ViewEnabledRole)
        assert enabled is True

        sample_city.sunset_data.hash_before_edit = None
        enabled = table_model.data(index, StatusActionDelegate.ViewEnabledRole)
        assert enabled is False

    def test_data_update_enabled_role(self, table_model, sample_city):
        """Тест роли включения кнопки обновления"""
        index = table_model.index(0, 7)

        sample_city.sunset_data.hash_before_edit = sample_city.get_stable_hash()
        sample_city.sunset_data.source = Source.CALCULATED
        enabled = table_model.data(index, StatusActionDelegate.ViewEnabledRole)
        assert enabled is True

        sample_city.sunset_data.source = Source.EDITED
        enabled = table_model.data(index, StatusActionDelegate.ViewEnabledRole)
        assert enabled is True

        sample_city.sunset_data.hash_before_edit = None
        enabled = table_model.data(index, StatusActionDelegate.ViewEnabledRole)
        assert enabled is False

    def test_data_invalid_index(self, table_model):
        """Тест получения данных для невалидного индекса"""
        invalid_index = QModelIndex()
        assert table_model.data(invalid_index) is None

    def test_set_data_check_state(self, table_model):
        """Тест установки состояния чекбокса"""
        index = table_model.index(0, 0)

        result = table_model.setData(
            index, Qt.CheckState.Checked.value, Qt.ItemDataRole.CheckStateRole
        )

        assert result is True
        assert table_model.checked_states[0] is True

    def test_set_data_edit_role(self, table_model):
        """Тест редактирования данных"""
        index = table_model.index(0, 1)

        new_name = "Новое название"
        result = table_model.setData(index, new_name, Qt.ItemDataRole.EditRole)

        assert result is True
        assert table_model.cities[0].name == new_name

    def test_set_data_edit_role_float(self, table_model):
        """Тест редактирования float значений"""
        index = table_model.index(0, 3)

        result = table_model.setData(index, "70.5", Qt.ItemDataRole.EditRole)

        assert result is True
        assert table_model.cities[0].lat == 70.5

        result = table_model.setData(index, "70,5", Qt.ItemDataRole.EditRole)

        assert result is True
        assert table_model.cities[0].lat == 70.5
