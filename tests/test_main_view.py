from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from sun_set.models.city import City
from sun_set.models.project_data import ProjectData
from sun_set.models.sunset import Source, YearData
from sun_set.models.table_model import STATUS_COLUMN
from sun_set.storage.city_json_storage import save_project_to_json
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
    project = ProjectData(
        year=2025,
        weekday1=4,
        weekday2=5,
        cities=[sample_city],
    )
    save_project_to_json(project, str(file_path))
    return str(file_path)


class TestMainWindow:
    def test_main_window_title(self, main_window):
        """Тест заголовка окна"""
        title = main_window.windowTitle()
        assert title.startswith("Sun Set")

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
        with patch("sun_set.views.main_view.choose_file", return_value=temp_json_file):
            main_window.open_file_dialog()

        assert main_window.file_path == temp_json_file

    def test_open_file_error(self, main_window, qtbot, temp_json_file, sample_city):
        project = ProjectData(
            year=2025,
            weekday1=4,
            weekday2=5,
            cities=[sample_city],
        )

        with patch("sun_set.views.main_view.choose_file") as mock_choose_file:
            mock_choose_file.side_effect = ["invalid_name.json", temp_json_file]

            with patch("sun_set.views.main_view.load_project") as mock_load:
                mock_load.side_effect = [
                    (None, "Ошибка: Файл не найден. Проверьте путь к файлу."),
                    (project, None),
                ]

                with patch("sun_set.views.main_view.ask_retry", return_value=True):
                    main_window.open_file_dialog()

        assert main_window.file_path == temp_json_file

    def test_open_file_updates_ui(self, main_window, qtbot, temp_json_file):
        """Тест обновления UI после открытия файла"""
        with patch("sun_set.views.main_view.choose_file", return_value=temp_json_file):
            main_window.open_file_dialog()

            # Таблица должна стать видимой
            assert main_window.table_view.isHidden() is False
            # Приглашение должно скрыться
            assert main_window.initial_prompt_text.isHidden() is True

    def test_apply_project_data(self, main_window, sample_city):
        project = ProjectData(
            year=2030,
            weekday1=1,
            weekday2=3,
            cities=[sample_city],
        )

        main_window.apply_project_data(project)

        assert main_window.year_spinbox.value() == 2030
        assert main_window.combo_weekday1.currentIndex() == 1
        assert main_window.combo_weekday2.currentIndex() == 3

    def test_save_file_with_valid_path(self, main_window, qtbot, temp_json_file):
        """Тест сохранения файла с существующим путем"""
        main_window.file_path = temp_json_file

        with patch("builtins.open", mock_open()):
            with patch("json.dump") as mock_dump:
                main_window.save_file()
                mock_dump.assert_called_once()

    def test_save_file_as_dialog(self, main_window, qtbot):
        """Тест диалога 'Сохранить как'"""
        with patch(
            "sun_set.views.main_view.choose_save_file", return_value="new_file.json"
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
        with patch("sun_set.views.main_view.choose_file", return_value=temp_json_file):
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

    @patch("sun_set.views.main_view.execute_sunset_update")
    def test_initiate_sunset_fetch_success(
        self, mock_execute_sunset_update, main_window
    ):
        """Тест успешного обновления выбранных городов и ресайза колонки статуса"""
        main_window.year_spinbox.setValue(2025)
        main_window.combo_weekday1.setCurrentIndex(0)
        main_window.combo_weekday2.setCurrentIndex(6)

        selected_cities = [MagicMock()]

        mock_model = MagicMock()
        mock_model.get_selected_cities.return_value = selected_cities
        main_window.model = mock_model

        main_window.table_view.resizeColumnToContents = MagicMock()

        main_window.initiate_sunset_fetch()

        request = mock_execute_sunset_update.call_args.args[0]

        assert request.year == 2025
        assert request.weekday1 == 0
        assert request.weekday2 == 6
        mock_model.clear_status_overrides_for_cities.assert_called_once_with(
            selected_cities
        )
        mock_model.refresh_status_column.assert_called_once()
        main_window.table_view.resizeColumnToContents.assert_called_once_with(
            STATUS_COLUMN
        )

    @patch("sun_set.views.main_view.show_warning")
    @patch("sun_set.views.main_view.execute_sunset_update")
    def test_initiate_sunset_fetch_no_updates(
        self,
        mock_execute_sunset_update,
        mock_show_warning,
        main_window,
    ):
        """Тест отсутствия обновления, если города не выбраны"""
        mock_model = MagicMock()
        mock_model.get_selected_cities.return_value = None
        main_window.model = mock_model

        main_window.table_view.resizeColumnToContents = MagicMock()

        main_window.initiate_sunset_fetch()

        mock_show_warning.assert_called_once_with(
            main_window,
            "Обновление данных",
            "Выберите хотя бы один город.",
        )
        mock_execute_sunset_update.assert_not_called()
        mock_model.clear_status_overrides_for_cities.assert_not_called()
        mock_model.refresh_status_column.assert_not_called()
        main_window.table_view.resizeColumnToContents.assert_not_called()

    def test_handle_city_update_logic(self, qtbot, main_window, temp_json_file):
        with patch("sun_set.views.main_view.choose_file", return_value=temp_json_file):
            main_window.open_file_dialog()

        mock_sunset_data = MagicMock()
        mock_sunset_data.get_stable_hash.return_value = "new_hash_123"

        with patch(
            "sun_set.services.city_service.get_city_sunset",
            return_value=mock_sunset_data,
        ) as mock_get:
            with qtbot.waitSignal(main_window.model.dataChanged):
                main_window.handle_city_update(0, "update")

        city = main_window.model.cities[0]
        mock_get.assert_called_once()
        assert city.sunset_data == mock_sunset_data
        assert city.sunset_data.hash_before_edit == city.get_stable_hash()

    def test_handle_city_update_view(self, qtbot, main_window, temp_json_file):
        with patch("sun_set.views.main_view.choose_file", return_value=temp_json_file):
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
        with patch("sun_set.views.main_view.choose_file", return_value=temp_json_file):
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
        with patch("sun_set.views.main_view.choose_file", return_value=temp_json_file):
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

    def test_apply_project_data_restores_export_paths(self, main_window):
        project = ProjectData(
            year=2026,
            weekday1=4,
            weekday2=5,
            cities=[],
            export_settings_path="/tmp/export_settings.json",
            export_output_dir="/tmp/export",
        )

        main_window.apply_project_data(project)

        assert (
            main_window.get_current_export_paths().settings_path
            == "/tmp/export_settings.json"
        )
        assert main_window.get_current_export_paths().output_dir == "/tmp/export"

        export_paths_text = main_window.export_paths_label.text()
        assert "export_settings.json" in export_paths_text
        assert "export" in export_paths_text

        export_paths_tooltip = main_window.export_paths_label.toolTip()
        assert "/tmp/export_settings.json" in export_paths_tooltip
        assert "/tmp/export" in export_paths_tooltip
