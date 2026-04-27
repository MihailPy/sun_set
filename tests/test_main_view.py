import json

import pytest
from PyQt6.QtWidgets import QApplication

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
    # window.show()
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
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump([sample_city], f)
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
        ],
    )
    def test_buttons_exist(self, main_window, btn_name):
        """Проверка существования кнопок"""
        assert getattr(main_window, btn_name) is not None
