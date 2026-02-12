# tests/test_file_manager.py
import json
import os
import tempfile
from unittest.mock import patch

import pytest

from sun_set.api.file_manager import load_from_json, save_to_json
from sun_set.models.city import City


@pytest.fixture
def sample_cities():
    """Фикстура с тестовыми городами"""
    return [
        City("Москва", "Московская обл.", 55.7558, 37.6173, "Europe/Moscow", 156),
        City(
            "Санкт-Петербург",
            "Ленинградская обл.",
            59.9343,
            30.3351,
            "Europe/Moscow",
            3,
        ),
        City(
            "Новосибирск",
            "Новосибирская обл.",
            55.0084,
            82.9357,
            "Asia/Novosibirsk",
            150,
        ),
    ]


@pytest.fixture
def temp_json_file():
    """Фикстура для временного JSON файла"""
    with tempfile.NamedTemporaryFile(
        mode="w+", suffix=".json", encoding="utf-8", delete=False
    ) as f:
        file_path = f.name
    yield file_path
    if os.path.exists(file_path):
        os.unlink(file_path)


# ============== ТЕСТЫ СОХРАНЕНИЯ ==============


def test_save_to_json_basic(sample_cities, temp_json_file):
    """Тест базового сохранения городов в JSON"""
    save_to_json(sample_cities, temp_json_file)

    assert os.path.exists(temp_json_file)

    with open(temp_json_file, encoding="utf-8") as f:
        data = json.load(f)

    assert len(data) == 3
    assert data[0]["name"] == "Москва"
    assert data[0]["lat"] == 55.7558


def test_save_to_json_empty_list(temp_json_file):
    """Тест сохранения пустого списка"""
    save_to_json([], temp_json_file)

    with open(temp_json_file, encoding="utf-8") as f:
        data = json.load(f)

    assert data == []


# ============== ТЕСТЫ ЗАГРУЗКИ ==============


def test_load_from_json_basic(sample_cities, temp_json_file):
    """Тест базовой загрузки городов из JSON"""
    save_to_json(sample_cities, temp_json_file)

    result = load_from_json(temp_json_file)
    cities, error = result

    assert error is None
    assert cities is not None
    assert len(cities) == 3
    assert isinstance(cities[0], City)
    assert cities[0].name == "Москва"


def test_load_from_json_empty_file(temp_json_file):
    """Тест загрузки из пустого JSON файла"""
    with open(temp_json_file, "w", encoding="utf-8") as f:
        f.write("[]")

    cities, error = load_from_json(temp_json_file)

    assert error is None
    assert cities is not None
    assert cities == []


def test_load_from_json_file_not_found():
    """Тест загрузки из несуществующего файла"""
    cities, error = load_from_json("/nonexistent/path/to/file.json")

    assert cities is None
    assert error is not None
    assert "Файл не найден" in error


def test_load_from_json_invalid_json(temp_json_file):
    """Тест загрузки из поврежденного JSON файла"""
    with open(temp_json_file, "w", encoding="utf-8") as f:
        f.write('{"name": "Москва", invalid json...}')

    cities, error = load_from_json(temp_json_file)

    assert cities is None
    assert error is not None
    assert "JSON" in error or "формат" in error


def test_load_from_json_permission_error():
    """Тест ошибки прав доступа при чтении"""
    with patch("builtins.open") as mock_open_func:
        mock_open_func.side_effect = PermissionError("Permission denied")

        cities, error = load_from_json("/protected/file.json")

        assert cities is None
        assert error is not None
        assert "Нет прав доступа" in error


# ============== ИНТЕГРАЦИОННЫЕ ТЕСТЫ ==============


def test_save_then_load_preserves_all_data(sample_cities, temp_json_file):
    """Тест полного цикла: сохранить -> загрузить -> проверить данные"""
    save_to_json(sample_cities, temp_json_file)

    result = load_from_json(temp_json_file)
    loaded_cities, error = result

    assert error is None
    assert loaded_cities is not None
    assert len(loaded_cities) == len(sample_cities)

    for original, loaded in zip(sample_cities, loaded_cities):
        assert loaded.name == original.name
        assert loaded.region == original.region
        assert loaded.lat == original.lat
        assert loaded.lon == original.lon
        assert loaded.timezone == original.timezone
        assert loaded.elevation == original.elevation


def test_save_then_load_with_various_values(temp_json_file):
    """Тест сохранения и загрузки разных типов значений"""
    cities = [
        City("", "", 0.0, 0.0, "", 0),
        City("A" * 100, "B" * 100, -90.0, -180.0, "UTC-12", -1000),
        City("  пробелы  ", "  ", 45.5, 45.5, "UTC+5:30", 5000),
    ]

    save_to_json(cities, temp_json_file)
    result = load_from_json(temp_json_file)
    loaded, error = result

    assert error is None
    assert loaded is not None
    assert loaded[0].name == ""
    assert loaded[1].lat == -90.0
    assert loaded[2].name == "  пробелы  "


def test_load_from_json_handles_all_exceptions(temp_json_file):
    """Тест что функция не падает с любыми ошибками"""
    with open(temp_json_file, "w", encoding="utf-8") as f:
        f.write("совсем не json")

    cities, error = load_from_json(temp_json_file)
    assert cities is None
    assert error is not None
