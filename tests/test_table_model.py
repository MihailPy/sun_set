from unittest.mock import Mock, patch

import pytest
from PyQt6.QtCore import QModelIndex, QPoint, QPointF, QRect, Qt
from PyQt6.QtGui import QMouseEvent, QPainter, QPixmap
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


class TestCheckBoxHeader:
    def test_initial_state(self, checkbox_header):
        """Тест начального состояния"""
        assert checkbox_header.is_checked is False

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
            initial_state = checkbox_header.is_checked
            checkbox_header.mousePressEvent(event)

            assert checkbox_header.is_checked != initial_state

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
            initial_state = checkbox_header.is_checked
            checkbox_header.mousePressEvent(event)

            assert checkbox_header.is_checked == initial_state


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

    def test_data_update_enabled_when_source_calculated(self, table_model, sample_city):
        """Тест роли включения кнопки обновления, когда данные собранны данные и не изменены."""
        index = table_model.index(0, 7)

        sample_city.sunset_data.hash_before_edit = sample_city.get_stable_hash()
        sample_city.sunset_data.source = Source.CALCULATED
        enabled = table_model.data(index, StatusActionDelegate.UpdateEnabledRole)
        assert enabled is False

    def test_data_update_enabled_when_source_edited(self, table_model, sample_city):
        """Тест роли включения кнопки обновления, когда данные были изменены."""
        index = table_model.index(0, 7)

        sample_city.sunset_data.hash_before_edit = sample_city.get_stable_hash()
        sample_city.sunset_data.source = Source.EDITED
        enabled = table_model.data(index, StatusActionDelegate.UpdateEnabledRole)
        assert enabled is True

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

    def test_set_data_invalid_value(self, table_model):
        """Тест установки невалидного значения"""
        index = table_model.index(0, 3)

        result = table_model.setData(index, "invalid", Qt.ItemDataRole.EditRole)

        assert result is False

    def test_set_data_status_override(self, table_model):
        """Тест переопределения статуса"""
        index = table_model.index(0, 7)

        result = table_model.setData(index, "Тестовый статус", Qt.ItemDataRole.EditRole)

        assert result is True
        assert table_model.status_overrides[0] == "Тестовый статус"

    def test_header_data(self, table_model):
        """Тест данных заголовка"""
        data = table_model.headerData(0, Qt.Orientation.Horizontal)
        assert data == ""

        data = table_model.headerData(1, Qt.Orientation.Horizontal)
        assert data == "Город"

        data = table_model.headerData(7, Qt.Orientation.Horizontal)
        assert data == "Данные заката"

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

        table_model.addCity(new_city)

        assert table_model.rowCount() == initial_count + 1
        assert table_model.cities[-1] == new_city
        assert len(table_model.checked_states) == initial_count + 1
        assert table_model.checked_states[-1] is False

    def test_select_all(self, table_model):
        """Тест выбора всех элементов"""
        table_model.selectAll(True)

        assert all(table_model.checked_states)

        table_model.selectAll(False)
        assert not any(table_model.checked_states)

    def test_remove_checked_cities(self, table_model):
        """Тест удаления отмеченных городов"""
        initial_count = table_model.rowCount()

        table_model.checked_states[0] = True

        table_model.removeCheckedCities()

        assert table_model.rowCount() == initial_count - 1
        assert len(table_model.cities) == initial_count - 1
        assert len(table_model.checked_states) == initial_count - 1

    @patch("sun_set.models.table_model.get_city_sunset")
    def test_update_checked_cities(self, mock_get_sunset, table_model, sample_city):
        """Тест обновления отмеченных городов"""
        mock_sunset_data = Mock(spec=YearData)
        mock_get_sunset.return_value = mock_sunset_data

        # Отмечаем первый город
        table_model.checked_states[0] = True

        updated_indices = table_model.updateCheckedCities(2024, 1, 2)

        assert updated_indices == [0]
        mock_get_sunset.assert_called_once_with(sample_city, 2024, 1, 2)
        assert table_model.cities[0].sunset_data == mock_sunset_data

    @patch("sun_set.models.table_model.get_city_sunset")
    def test_handle_button_click_update(
        self, mock_get_sunset, table_model, sample_city
    ):
        """Тест обработки клика по кнопке обновления"""
        mock_sunset_data = Mock(spec=YearData)
        mock_get_sunset.return_value = mock_sunset_data

        sample_city.sunset_data.hash_before_edit = "old_hash"

        table_model.handleButtonClick(0, "update")

        mock_get_sunset.assert_called_once()
        assert sample_city.sunset_data == mock_sunset_data

    def test_handle_button_click_view(self, table_model, capsys):
        """Тест обработки клика по кнопке просмотра"""
        table_model.handleButtonClick(0, "view")

        captured = capsys.readouterr()
        assert "Просмотр города: Москва" in captured.out

    def test_data_changed_signal(self, table_model):
        """Тест сигнала об изменении данных"""
        signal_received = False

        def on_data_changed(*args):
            nonlocal signal_received
            signal_received = True

        table_model.dataChanged.connect(on_data_changed)

        index = table_model.index(0, 1)
        table_model.setData(index, "Новое имя", Qt.ItemDataRole.EditRole)

        assert signal_received is True
