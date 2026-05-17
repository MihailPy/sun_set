import json
from pathlib import Path

import pytest

from sun_set.image_export.settings import (
    ExportImageSettings,
    ImageSettings,
    load_export_settings,
)


@pytest.fixture
def valid_settings_dict():
    """Фикстура с корректными данными в формате словаря."""
    return {
        "image": {
            "width": 1920,
            "height": 1080,
            "background_color": "#ffffff",
            "template_path": None,
        },
        "text": {"font_path": None, "font_size": 24, "color": "#000000"},
        "layout": {
            "row_height": 50,
            "first_column_offset_x": 10,
            "second_column_offset_x": 20,
            "month_blocks": {"1": {"x": 100, "y": 200}, "2": {"x": 150, "y": 250}},
        },
    }


def test_load_export_settings_success(tmp_path: Path, valid_settings_dict):
    """Проверяем успешную загрузку и корректность типов."""
    # Создаем временный JSON файл
    config_file = tmp_path / "settings.json"
    config_file.write_text(json.dumps(valid_settings_dict), encoding="utf-8")

    settings = load_export_settings(config_file)

    # Проверяем структуру
    assert isinstance(settings, ExportImageSettings)
    assert isinstance(settings.image, ImageSettings)
    assert settings.image.width == 1920
    assert settings.layout.month_blocks[1].x == 100
    assert isinstance(settings.layout.row_height, int)


def test_load_export_settings_optional_fields(tmp_path, valid_settings_dict):
    """Проверяем работу с полями, которые могут быть None."""
    valid_settings_dict["image"]["template_path"] = None
    valid_settings_dict["text"]["font_path"] = None

    config_file = tmp_path / "settings_none.json"
    config_file.write_text(json.dumps(valid_settings_dict), encoding="utf-8")

    settings = load_export_settings(config_file)
    assert settings.image.template_path is None
    assert settings.text.font_path is None


def test_load_export_settings_invalid_json(tmp_path):
    """Проверяем реакцию на битый JSON файл."""
    bad_file = tmp_path / "broken.json"
    bad_file.write_text("{ invalid json }", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        load_export_settings(bad_file)


def test_load_export_settings_missing_keys(tmp_path):
    """Проверяем реакцию на отсутствие обязательных полей."""
    incomplete_data = {"image": {"width": 100}}  # не хватает кучи полей
    config_file = tmp_path / "incomplete.json"
    config_file.write_text(json.dumps(incomplete_data), encoding="utf-8")

    # dacite выбросит ошибку, если не найдет нужных ключей для датакласса
    with pytest.raises(Exception):
        load_export_settings(config_file)


def test_load_example_default_white_settings():
    settings_path = Path("examples/image_export/default_white.json")

    settings = load_export_settings(settings_path)

    assert settings.image.width == 2384
    assert settings.image.height == 3508
    assert settings.layout.month_blocks[1].x == 100
