from PIL import Image
from PyQt6.QtWidgets import QMessageBox

from sun_set.image_export.service import build_city_image_preview_from_settings
from sun_set.image_export.settings import (
    create_default_export_settings,
    load_export_settings,
    validate_export_settings,
)
from sun_set.views.image_export_settings_dialog import ImageExportSettingsDialog


def test_image_export_settings_dialog_created(qtbot, export_settings):
    dialog = ImageExportSettingsDialog(settings=export_settings)

    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Настройки экспорта изображения"


def test_image_export_settings_dialog_fields_filled(qtbot, export_settings):
    dialog = ImageExportSettingsDialog(settings=export_settings)

    qtbot.addWidget(dialog)

    assert dialog.width_spin.value() == export_settings.image.width
    assert dialog.height_spin.value() == export_settings.image.height
    assert dialog.font_size_spin.value() == export_settings.text.font_size
    assert dialog.row_height_spin.value() == export_settings.layout.row_height


def test_image_export_settings_dialog_updates_month_position(qtbot, export_settings):
    dialog = ImageExportSettingsDialog(settings=export_settings)

    qtbot.addWidget(dialog)

    dialog.month_combo.setCurrentIndex(0)  # месяц 1
    dialog.month_x_spin.setValue(123)
    dialog.month_y_spin.setValue(456)

    assert export_settings.layout.month_blocks[1].x == 123
    assert export_settings.layout.month_blocks[1].y == 456


def test_image_export_settings_dialog_shifts_all_months(qtbot, export_settings):
    dialog = ImageExportSettingsDialog(settings=export_settings)

    qtbot.addWidget(dialog)

    old_x = export_settings.layout.month_blocks[1].x
    old_y = export_settings.layout.month_blocks[1].y

    dialog.shift_x_spin.setValue(10)
    dialog.shift_y_spin.setValue(20)
    dialog.shift_all_months()

    assert export_settings.layout.month_blocks[1].x == old_x + 10
    assert export_settings.layout.month_blocks[1].y == old_y + 20


def test_image_export_settings_dialog_copies_month_position(qtbot, export_settings):
    dialog = ImageExportSettingsDialog(settings=export_settings)

    qtbot.addWidget(dialog)

    export_settings.layout.month_blocks[1].x = 111
    export_settings.layout.month_blocks[1].y = 222

    dialog.copy_source_month_combo.setCurrentIndex(0)  # 1
    dialog.copy_target_month_combo.setCurrentIndex(1)  # 2

    dialog.copy_month_position()

    assert export_settings.layout.month_blocks[2].x == 111
    assert export_settings.layout.month_blocks[2].y == 222


def test_image_export_settings_dialog_save_to_path(
    qtbot,
    export_settings,
    tmp_path,
):
    dialog = ImageExportSettingsDialog(settings=export_settings)
    qtbot.addWidget(dialog)

    dialog.width_spin.setValue(777)

    settings_path = tmp_path / "settings.json"

    dialog.save_to_path(settings_path)

    loaded_settings = load_export_settings(settings_path)

    assert loaded_settings.image.width == 777


def test_create_default_export_settings_is_valid():
    settings = create_default_export_settings()

    validate_export_settings(settings)

    assert settings.image.width == 1000
    assert len(settings.layout.month_blocks) == 12


def test_build_city_image_preview_from_settings_returns_image(
    test_city,
    export_settings,
):
    image = build_city_image_preview_from_settings(
        city=test_city,
        settings=export_settings,
    )

    assert isinstance(image, Image.Image)


def test_image_export_settings_dialog_has_preview_widgets(qtbot, export_settings):
    dialog = ImageExportSettingsDialog(settings=export_settings)

    qtbot.addWidget(dialog)

    assert dialog.preview_label is not None
    assert dialog.preview_scroll_area is not None
    assert dialog.preview_scale_combo is not None


def test_image_export_settings_dialog_set_preview_image(qtbot, export_settings):
    dialog = ImageExportSettingsDialog(settings=export_settings)

    qtbot.addWidget(dialog)

    image = Image.new("RGB", (100, 200), "#ffffff")

    dialog.set_preview_image(image)

    assert dialog.current_preview_image is image
    assert dialog.preview_label.pixmap() is not None


def test_image_export_settings_dialog_refresh_preview_pixmap_with_scale(
    qtbot,
    export_settings,
):
    dialog = ImageExportSettingsDialog(settings=export_settings)

    qtbot.addWidget(dialog)

    image = Image.new("RGB", (100, 200), "#ffffff")
    dialog.set_preview_image(image)

    dialog.preview_scale_combo.setCurrentText("50%")
    dialog.refresh_preview_pixmap()

    pixmap = dialog.preview_label.pixmap()

    assert pixmap is not None
    assert pixmap.width() == 50
    assert pixmap.height() == 100


def test_image_export_settings_dialog_update_preview_without_city(
    qtbot,
    export_settings,
):
    dialog = ImageExportSettingsDialog(settings=export_settings, city=None)

    qtbot.addWidget(dialog)

    dialog.update_preview()

    assert dialog.preview_label.text() == "Выберите город для предпросмотра."


def test_save_settings_as_uses_correct_dialog_arguments(
    qtbot,
    monkeypatch,
    export_settings,
    tmp_path,
):
    dialog = ImageExportSettingsDialog(export_settings)
    qtbot.addWidget(dialog)

    target_path = tmp_path / "settings.json"
    captured = {}

    def fake_choose_save_file(
        parent,
        title,
        file_filter,
        initial_path="",
    ):
        captured["title"] = title
        captured["file_filter"] = file_filter
        captured["initial_path"] = initial_path
        return str(target_path)

    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.choose_save_file",
        fake_choose_save_file,
    )

    monkeypatch.setattr(dialog, "save_settings", lambda: None)

    dialog.save_settings_as()

    assert captured["file_filter"] == "JSON files (*.json)"
    assert captured["initial_path"] == ""
    assert dialog.settings_path == target_path


def test_save_settings_as_adds_json_suffix(
    qtbot,
    monkeypatch,
    export_settings,
    tmp_path,
):
    dialog = ImageExportSettingsDialog(export_settings)
    qtbot.addWidget(dialog)

    target_path = tmp_path / "settings"

    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.choose_save_file",
        lambda *args, **kwargs: str(target_path),
    )
    monkeypatch.setattr(dialog, "save_settings", lambda: None)

    dialog.save_settings_as()

    assert dialog.settings_path == target_path.with_suffix(".json")


def test_dialog_initially_has_no_unsaved_changes(qtbot, export_settings):
    dialog = ImageExportSettingsDialog(export_settings)
    qtbot.addWidget(dialog)

    assert dialog.is_dirty is False
    assert dialog.windowTitle() == dialog.WINDOW_TITLE


def test_dialog_marks_changes_in_window_title(qtbot, export_settings):
    dialog = ImageExportSettingsDialog(export_settings)
    qtbot.addWidget(dialog)

    dialog.width_spin.setValue(dialog.width_spin.value() + 1)

    assert dialog.is_dirty is True
    assert dialog.windowTitle() == f"{dialog.WINDOW_TITLE} *"


def test_dialog_becomes_clean_after_save(
    qtbot,
    monkeypatch,
    export_settings,
    tmp_path,
):
    dialog = ImageExportSettingsDialog(
        export_settings,
        settings_path=tmp_path / "settings.json",
    )
    qtbot.addWidget(dialog)

    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.save_export_settings",
        lambda *args, **kwargs: None,
    )
    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.show_information",
        lambda *args, **kwargs: None,
    )

    dialog.width_spin.setValue(dialog.width_spin.value() + 1)

    assert dialog.is_dirty is True

    dialog.save_settings()

    assert dialog.is_dirty is False
    assert dialog.windowTitle() == dialog.WINDOW_TITLE


def test_dialog_stays_dirty_when_save_fails(
    qtbot,
    monkeypatch,
    export_settings,
    tmp_path,
):
    dialog = ImageExportSettingsDialog(
        export_settings,
        settings_path=tmp_path / "settings.json",
    )
    qtbot.addWidget(dialog)

    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.save_export_settings",
        lambda *args, **kwargs: (_ for _ in ()).throw(OSError("save failed")),
    )
    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.show_error",
        lambda *args, **kwargs: None,
    )

    dialog.width_spin.setValue(dialog.width_spin.value() + 1)
    dialog.save_settings()

    assert dialog.is_dirty is True
    assert dialog.windowTitle() == f"{dialog.WINDOW_TITLE} *"


def test_clean_dialog_closes_without_confirmation(
    qtbot,
    monkeypatch,
    export_settings,
):
    dialog = ImageExportSettingsDialog(export_settings)
    qtbot.addWidget(dialog)

    def unexpected_confirmation(*args, **kwargs):
        raise AssertionError("Confirmation should not be shown")

    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.ask_save_discard_cancel",
        unexpected_confirmation,
    )

    assert dialog.confirm_close() is True


def test_dirty_dialog_can_discard_changes(
    qtbot,
    monkeypatch,
    export_settings,
):
    dialog = ImageExportSettingsDialog(export_settings)
    qtbot.addWidget(dialog)

    dialog.width_spin.setValue(dialog.width_spin.value() + 1)

    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.ask_save_discard_cancel",
        lambda *args, **kwargs: QMessageBox.StandardButton.Discard,
    )

    assert dialog.confirm_close() is True


def test_dirty_dialog_can_cancel_close(
    qtbot,
    monkeypatch,
    export_settings,
):
    dialog = ImageExportSettingsDialog(export_settings)
    qtbot.addWidget(dialog)

    dialog.width_spin.setValue(dialog.width_spin.value() + 1)

    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.ask_save_discard_cancel",
        lambda *args, **kwargs: QMessageBox.StandardButton.Cancel,
    )

    assert dialog.confirm_close() is False
    assert dialog.is_dirty is True


def test_dirty_dialog_closes_after_successful_save(
    qtbot,
    monkeypatch,
    export_settings,
):
    dialog = ImageExportSettingsDialog(export_settings)
    qtbot.addWidget(dialog)

    dialog.width_spin.setValue(dialog.width_spin.value() + 1)

    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.ask_save_discard_cancel",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save,
    )
    monkeypatch.setattr(dialog, "save_settings", lambda: True)

    assert dialog.confirm_close() is True


def test_dirty_dialog_stays_open_when_save_is_cancelled(
    qtbot,
    monkeypatch,
    export_settings,
):
    dialog = ImageExportSettingsDialog(export_settings)
    qtbot.addWidget(dialog)

    dialog.width_spin.setValue(dialog.width_spin.value() + 1)

    monkeypatch.setattr(
        "sun_set.views.image_export_settings_dialog.ask_save_discard_cancel",
        lambda *args, **kwargs: QMessageBox.StandardButton.Save,
    )
    monkeypatch.setattr(dialog, "save_settings", lambda: False)

    assert dialog.confirm_close() is False
