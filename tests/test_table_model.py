from unittest.mock import Mock, patch

import pytest
from PyQt6.QtCore import QModelIndex, QPoint, QPointF, QRect, Qt
from PyQt6.QtGui import QMouseEvent, QPainter, QPixmap
from PyQt6.QtWidgets import QApplication

from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData
from sun_set.models.table_model import (
    CHECK_COLUMN,
    CITY_NAME_COLUMN,
    LAT_COLUMN,
    REGION_COLUMN,
    STATUS_COLUMN,
    SUNSET_DATA_COLUMN,
    CheckBoxHeader,
    CityTableModel,
    parse_float_cell_value,
    parse_int_cell_value,
)
from sun_set.services.city_service import update_cities_sunset


@pytest.fixture
def qapp():
    """Создает QApplication для тестов"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


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
def checkbox_header(qapp):
    header = CheckBoxHeader(Qt.Orientation.Horizontal)
    header.setModel(CityTableModel([]))
    return header


class TestCheckBoxHeader:
    def test_initial_state(self, checkbox_header):
        """Тест начального состояния"""
        assert checkbox_header.is_all_rows_selected is False

    def test_paint_section_with_null_painter(self, checkbox_header):
        """Тест отрисовки с None painter"""
        rect = QRect(0, 0, 100, 30)

        checkbox_header.paintSection(None, rect, 0)

    def test_paint_section_checkbox(self, checkbox_header, qapp, mocker):
        """Тест отрисовки чекбокса"""
        pixmap = QPixmap(100, 30)
        painter = QPainter(pixmap)
        save_spy = mocker.spy(painter, "save")
        restore_spy = mocker.spy(painter, "restore")

        rect = QRect(0, 0, 100, 30)

        checkbox_header.paintSection(painter, rect, 0)
        painter.end()

        assert save_spy.called
        assert restore_spy.called

    def test_mouse_press_event_on_checkbox(self, checkbox_header, table_model):
        """Тест клика по чекбоксу в заголовке"""
        checkbox_header.setModel(table_model)

        event = Mock(spec=QMouseEvent)
        event.pos.return_value = QPoint(10, 10)

        with patch.object(CheckBoxHeader, "logicalIndexAt", return_value=0):
            initial_state = checkbox_header.is_all_rows_selected
            checkbox_header.mousePressEvent(event)

            assert checkbox_header.is_all_rows_selected != initial_state

    def test_mouse_press_event_other_column(self, checkbox_header):
        """Тест клика по другой колонке"""
        event = QMouseEvent(
            QMouseEvent.Type.MouseButtonPress,
            QPointF(200, 10),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )

        with patch.object(CheckBoxHeader, "logicalIndexAt", return_value=1):
            initial_state = checkbox_header.is_all_rows_selected
            checkbox_header.mousePressEvent(event)

            assert checkbox_header.is_all_rows_selected == initial_state

    def test_mouse_press_event_null(self, checkbox_header):
        """Тест с None событием"""
        checkbox_header.mousePressEvent(None)


class TestCityTableModel:
    def test_row_count(self, table_model, sample_cities):
        """Тест количества строк"""
        assert table_model.rowCount() == len(sample_cities)

    def test_column_count(self, table_model):
        """Тест количества колонок"""
        assert table_model.columnCount() == 9

    def test_flags(self, table_model):
        """Тест флагов для разных колонок"""
        # Колонка с чекбоксом
        index = table_model.index(0, CHECK_COLUMN)
        flags = table_model.flags(index)
        assert flags & Qt.ItemFlag.ItemIsUserCheckable

        # Колонка с кнопками
        index = table_model.index(0, STATUS_COLUMN)
        flags = table_model.flags(index)
        assert flags & Qt.ItemFlag.ItemIsEnabled

        # Обычная колонка
        index = table_model.index(0, CITY_NAME_COLUMN)
        flags = table_model.flags(index)
        assert flags & Qt.ItemFlag.ItemIsEditable

    def test_data_display_role(self, table_model, sample_city):
        """Тест получения данных для отображения"""
        index = table_model.index(0, CITY_NAME_COLUMN)
        assert table_model.data(index, Qt.ItemDataRole.DisplayRole) == sample_city.name

        index = table_model.index(0, REGION_COLUMN)
        assert (
            table_model.data(index, Qt.ItemDataRole.DisplayRole) == sample_city.region
        )

        index = table_model.index(0, LAT_COLUMN)
        assert table_model.data(index, Qt.ItemDataRole.DisplayRole) == str(
            sample_city.lat
        )

    def test_data_check_state_role(self, table_model):
        """Тест состояния чекбокса"""
        index = table_model.index(0, CHECK_COLUMN)

        state = table_model.data(index, Qt.ItemDataRole.CheckStateRole)
        assert state == Qt.CheckState.Unchecked

        table_model.selected_rows[0] = True
        state = table_model.data(index, Qt.ItemDataRole.CheckStateRole)
        assert state == Qt.CheckState.Checked

    def test_data_status_column(self, table_model, sample_city):
        index = table_model.index(0, STATUS_COLUMN)

        sample_city.sunset_data.hash_before_edit = sample_city.get_stable_hash()
        sample_city.sunset_data.source = Source.CALCULATED

        status = table_model.data(index, Qt.ItemDataRole.DisplayRole)

        assert status == "Актуально"

    def test_data_sunset_data_column(self, table_model, sample_city):
        sample_city.sunset_data.months = {"1": []}
        index = table_model.index(0, SUNSET_DATA_COLUMN)

        action_text = table_model.data(index, Qt.ItemDataRole.DisplayRole)

        assert action_text == "Открыть"

    def test_data_invalid_index(self, table_model):
        """Тест получения данных для невалидного индекса"""
        invalid_index = QModelIndex()
        assert table_model.data(invalid_index) is None

    def test_set_data_check_state(self, table_model):
        """Тест установки состояния чекбокса"""
        index = table_model.index(0, CHECK_COLUMN)

        result = table_model.setData(
            index, Qt.CheckState.Checked.value, Qt.ItemDataRole.CheckStateRole
        )

        assert result is True
        assert table_model.selected_rows[0] is True

    def test_set_data_edit_role(self, table_model):
        """Тест редактирования данных"""
        index = table_model.index(0, CITY_NAME_COLUMN)

        new_name = "Новое название"
        result = table_model.setData(index, new_name, Qt.ItemDataRole.EditRole)

        assert result is True
        assert table_model.cities[0].name == new_name

    def test_set_data_edit_role_float(self, table_model):
        """Тест редактирования float значений"""
        index = table_model.index(0, LAT_COLUMN)

        result = table_model.setData(index, "70.5", Qt.ItemDataRole.EditRole)

        assert result is True
        assert table_model.cities[0].lat == 70.5

        result = table_model.setData(index, "70,5", Qt.ItemDataRole.EditRole)

        assert result is True
        assert table_model.cities[0].lat == 70.5

    def test_set_data_invalid_value(self, table_model):
        """Тест установки невалидного значения"""
        index = table_model.index(0, LAT_COLUMN)

        result = table_model.setData(index, "invalid", Qt.ItemDataRole.EditRole)

        assert result is False

    def test_header_data(self, table_model):
        """Тест данных заголовка"""
        data = table_model.headerData(0, Qt.Orientation.Horizontal)
        assert data == ""

        data = table_model.headerData(1, Qt.Orientation.Horizontal)
        assert data == "Город"

        data = table_model.headerData(7, Qt.Orientation.Horizontal)
        assert data == "Статус"

    def test_table_headers_include_status_and_sunset_data(self, table_model):
        status_header = table_model.headerData(
            STATUS_COLUMN,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.DisplayRole,
        )
        sunset_data_header = table_model.headerData(
            SUNSET_DATA_COLUMN,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.DisplayRole,
        )

        assert status_header == "Статус"
        assert sunset_data_header == "Данные заката"

    def test_add_city(self, table_model):
        """Тест добавления города"""
        initial_count = table_model.rowCount()
        new_city = City(
            name="Казань",
            region="Татарстан",
            lat=55.7887,
            lon=49.1221,
            timezone="Europe/Moscow",
            elevation=116,
            sunset_data=YearData(2033, Source.CALCULATED, None, None),
        )

        table_model.add_city(new_city)

        assert table_model.rowCount() == initial_count + 1
        assert table_model.cities[-1] == new_city
        assert len(table_model.selected_rows) == initial_count + 1
        assert table_model.selected_rows[-1] is False

    def test_set_all_rows_selected(self, table_model):
        """Тест выбора всех элементов"""
        table_model.set_all_rows_selected(True)

        assert all(table_model.selected_rows)

        table_model.set_all_rows_selected(False)
        assert not any(table_model.selected_rows)

    def test_remove_selected_cities(self, table_model):
        """Тест удаления отмеченных городов"""
        initial_count = table_model.rowCount()

        table_model.selected_rows[0] = True

        table_model.remove_selected_cities()

        assert table_model.rowCount() == initial_count - 1
        assert len(table_model.cities) == initial_count - 1
        assert len(table_model.selected_rows) == initial_count - 1

    @patch("sun_set.services.city_service.get_city_sunset")
    def test_update_cities_sunset(self, mock_get_sunset, sample_city):
        """Тест обновления списка городов"""
        mock_sunset_data = Mock(spec=YearData)
        mock_get_sunset.return_value = mock_sunset_data

        update_cities_sunset([sample_city], 2024, 1, 2)

        mock_get_sunset.assert_called_once_with(sample_city, 2024, 1, 2)
        assert sample_city.sunset_data == mock_sunset_data
        assert sample_city.sunset_data.hash_before_edit == sample_city.get_stable_hash()

    def test_data_changed_signal(self, table_model):
        """Тест сигнала об изменении данных"""
        signal_received = False

        def on_data_changed(*args):
            nonlocal signal_received
            signal_received = True

        table_model.dataChanged.connect(on_data_changed)

        index = table_model.index(0, CITY_NAME_COLUMN)
        table_model.setData(index, "Новое имя", Qt.ItemDataRole.EditRole)

        assert signal_received is True

    def test_sunset_data_column_foreground_role(self, table_model, sample_city):
        sample_city.sunset_data.months = {"1": []}
        index = table_model.index(0, SUNSET_DATA_COLUMN)

        color = table_model.data(index, Qt.ItemDataRole.ForegroundRole)

        assert color is not None

    def test_sunset_data_column_font_role(self, table_model, sample_city):
        sample_city.sunset_data.months = {"1": []}
        index = table_model.index(0, SUNSET_DATA_COLUMN)

        font = table_model.data(index, Qt.ItemDataRole.FontRole)

        assert font is not None
        assert font.underline()

    def test_data_sunset_data_column_without_data(self, table_model, sample_city):
        sample_city.sunset_data.months = {}
        index = table_model.index(0, SUNSET_DATA_COLUMN)

        assert table_model.data(index, Qt.ItemDataRole.DisplayRole) == ""

    def test_get_selected_row_indexes(self, table_model, sample_city):
        table_model.cities.append(sample_city)
        table_model.cities.append(sample_city)
        table_model.selected_rows = [True, False, True]

        assert table_model.get_selected_row_indexes() == [0, 2]


def test_parse_float_cell_value_with_dot():
    assert parse_float_cell_value("55.75") == 55.75


def test_parse_float_cell_value_with_comma():
    assert parse_float_cell_value("55,75") == 55.75


def test_parse_int_cell_value():
    assert parse_int_cell_value("150") == 150
