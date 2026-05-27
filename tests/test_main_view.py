from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QFileDialog

from sun_set.api.file_manager import save_to_json
from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData
from sun_set.views.main_view import MainWindow


@pytest.fixture(scope="session")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(qtbot):
    """Базовая фикстура для MainWindow"""
    window = MainWindow()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    yield window
    window.close()


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
def temp_json_file(tmp_path, sample_city):
    file_path = tmp_path / "test_cities.json"
    save_to_json([sample_city], str(file_path))
    return str(file_path)


class TestMainWindow:
    def test_main_window_title(self, main_window):
        """Тест заголовка окна"""
        assert main_window.windowTitle() == "Sun set"

    @pytest.mark.parametrize(
        "btn_name",
        [
            "btn_choose_file",
            "btn_save_file",
            "btn_save_file_as",
            "btn_add_city",
            "btn_del_city",
            "btn_get_sunset_info",
            "btn_export_image",
        ],
    )
    def test_buttons_exist(self, main_window, btn_name):
        """Проверка существования кнопок"""
        assert getattr(main_window, btn_name) is not None

    def test_initial_prompt_visible(self, main_window):
        """Тест видимости начального приглашения"""
        assert main_window.initial_prompt_text.isVisible() is True

    def test_open_file_dialog_called(self, main_window, qtbot, temp_json_file):
        """Тест открытия файла через диалог"""
        with patch.object(
            QFileDialog, "getOpenFileName", return_value=(temp_json_file, "")
        ):
            main_window.open_file_dialog()
            assert main_window.file_path == temp_json_file

    def test_open_file_error(self, main_window, qtbot, temp_json_file, sample_city):
        """Тест вывода окна с ошибкой, если при открытии файла произошла ошибка"""
        with patch("PyQt6.QtWidgets.QFileDialog.getOpenFileName") as mock_file:
            mock_file.side_effect = [("invalid_name.json", ""), (temp_json_file, "")]

            with patch(
                "sun_set.views.main_view.load_from_json",
            ) as mock_load:
                mock_load.side_effect = [
                    (None, "Ошибка: Файл не найден. Проверьте путь к файлу."),
                    ([sample_city], None),
                ]

    def test_open_file_updates_ui(self, main_window, qtbot, temp_json_file):
        """Тест обновления UI после открытия файла"""
        with patch.object(
            QFileDialog, "getOpenFileName", return_value=(temp_json_file, "")
        ):
            main_window.open_file_dialog()

            # Таблица должна стать видимой
            assert main_window.table_view.isHidden() is False
            # Приглашение должно скрыться
            assert main_window.initial_prompt_text.isHidden() is True

    def test_save_file_with_valid_path(self, main_window, qtbot, temp_json_file):
        """Тест сохранения файла с существующим путем"""
        main_window.file_path = temp_json_file

        with patch("builtins.open", mock_open()):
            with patch("json.dump") as mock_dump:
                main_window.save_file()
                mock_dump.assert_called_once()

    def test_save_file_as_dialog(self, main_window, qtbot):
        """Тест диалога 'Сохранить как'"""
        with patch.object(
            QFileDialog, "getSaveFileName", return_value=("new_file.json", "")
        ):
            with patch("builtins.open", mock_open()):
                main_window.save_file_as()
                assert main_window.file_path == "new_file.json"

    def test_add_city(self, main_window, qtbot):
        """Тест добавления городов"""
        assert main_window.table_view.isHidden()
        assert main_window.initial_prompt_text.isVisible()

        qtbot.mouseClick(main_window.btn_add_city, Qt.MouseButton.LeftButton)

        assert main_window.model is not None
        assert main_window.model.rowCount() == 1
        assert main_window.table_view.isVisible()
        assert main_window.initial_prompt_text.isHidden()

        qtbot.mouseClick(main_window.btn_add_city, Qt.MouseButton.LeftButton)
        assert main_window.model.rowCount() == 2

    def test_delete_selected_cities(self, main_window, qtbot, temp_json_file):
        """Тест удаления выбранных городов через чекбокс"""
        with patch.object(
            QFileDialog, "getOpenFileName", return_value=(temp_json_file, "")
        ):
            main_window.open_file_dialog()

        model = main_window.table_view.model()
        initial_count = model.rowCount()

        index = model.index(0, 0)
        model.setData(index, Qt.CheckState.Checked, Qt.ItemDataRole.CheckStateRole)

        qtbot.mouseClick(main_window.btn_del_city, Qt.MouseButton.LeftButton)
        # main_window.delete_selected_cities()

        assert model.rowCount() == initial_count - 1

    def test_year_spinbox_range(self, main_window):
        """Тест диапазона спинбокса года"""
        current_year = datetime.now().year
        assert main_window.year_spinbox.minimum() == current_year - 50
        assert main_window.year_spinbox.maximum() == current_year + 50
        assert main_window.year_spinbox.value() == current_year + 1

    def test_weekday_combos_initial_state(self, main_window):
        """Тест начального состояния комбобоксов дней недели"""
        assert main_window.combo_weekday1.currentData() == 4  # Пятница
        assert main_window.combo_weekday2.currentData() == 5  # Суббота

    def test_weekday_combos_items(self, main_window):
        """Тест содержимого комбобоксов дней недели"""
        expected_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        for i, expected_day in enumerate(expected_days):
            assert main_window.combo_weekday1.itemText(i) == expected_day
            assert main_window.combo_weekday2.itemText(i) == expected_day

    def test_initiate_sunset_fetch_success(self, main_window):
        """Тест успешного обновления данных и ресайза колонок"""
        main_window.year_spinbox.setValue(2025)
        main_window.combo_weekday1.setCurrentIndex(0)
        main_window.combo_weekday2.setCurrentIndex(6)

        mock_model = MagicMock()
        main_window.model = mock_model

        mock_model.update_checked_cities.return_value = 5

        main_window.table_view.resizeColumnToContents = MagicMock()

        main_window.initiate_sunset_fetch()

        mock_model.update_checked_cities.assert_called_once_with(2025, 0, 6)

        main_window.table_view.resizeColumnToContents.assert_called_once_with(7)

    def test_initiate_sunset_fetch_no_updates(self, main_window):
        """Тест отсутствия ресайза при пустом обновлении"""
        main_window.model = MagicMock()
        main_window.model.update_checked_cities.return_value = 0
        main_window.table_view.resizeColumnToContents = MagicMock()

        main_window.initiate_sunset_fetch()

        main_window.table_view.resizeColumnToContents.assert_not_called()

    def test_handle_city_update_logic(self, qtbot, main_window, temp_json_file):
        with patch(
            "PyQt6.QtWidgets.QFileDialog.getOpenFileName",
            return_value=(temp_json_file, ""),
        ):
            main_window.open_file_dialog()

        mock_sunset_data = MagicMock()
        mock_sunset_data.get_stable_hash.return_value = "new_hash_123"

        with patch(
            "sun_set.views.main_view.get_city_sunset", return_value=mock_sunset_data
        ) as mock_get:
            with qtbot.waitSignal(main_window.model.dataChanged):
                main_window.handle_city_update(0, "update")

        city = main_window.model.cities[0]
        mock_get.assert_called_once()
        assert city.sunset_data == mock_sunset_data
        assert city.sunset_data.hash_before_edit == city.get_stable_hash()

    def test_handle_city_update_view(self, qtbot, main_window, temp_json_file):
        with patch(
            "PyQt6.QtWidgets.QFileDialog.getOpenFileName",
            return_value=(temp_json_file, ""),
        ):
            main_window.open_file_dialog()

        city = main_window.model.cities[0]

        mock_sunset_data = MagicMock()
        mock_sunset_data.months = [MagicMock() for _ in range(12)]
        city.sunset_data = mock_sunset_data

        main_window.handle_city_update(0, "view")

        assert main_window.extra_window is not None
        assert main_window.extra_window.isVisible()

        with patch.object(main_window, "on_city_data_changed") as mock_on_changed:
            main_window.extra_window.dataChanged.emit()
            mock_on_changed.assert_called_once_with(0)

    def test_on_city_data_changed_updates_hash_and_ui(
        self, qtbot, main_window, temp_json_file
    ):
        with patch(
            "PyQt6.QtWidgets.QFileDialog.getOpenFileName",
            return_value=(temp_json_file, ""),
        ):
            main_window.open_file_dialog()

        city = main_window.model.cities[0]
        city.get_stable_hash = MagicMock(return_value="updated_hash_456")

        with qtbot.waitSignal(main_window.model.dataChanged) as blocker:
            main_window.on_city_data_changed(0)

        assert city.sunset_data.hash_before_edit == "updated_hash_456"

        index_from, _, roles = blocker.args
        assert index_from.row() == 0
        assert index_from.column() == 7
        assert Qt.ItemDataRole.DisplayRole in roles

    def test_full_workflow(self, main_window, qtbot, temp_json_file):
        """Интеграционный тест полного рабочего процесса"""
        # 1. Открываем файл
        with patch.object(
            QFileDialog, "getOpenFileName", return_value=(temp_json_file, "")
        ):
            main_window.open_file_dialog()

        # 2. Проверяем что данные загрузились
        assert main_window.table_view.model().rowCount() > 0
        assert not main_window.table_view.isHidden()

        # 3. Настраиваем даты
        main_window.year_spinbox.setValue(2025)
        main_window.combo_weekday1.setCurrentIndex(5)

        # 4. Проверяем сохранение
        with patch("builtins.open", mock_open()):
            main_window.save_file()
