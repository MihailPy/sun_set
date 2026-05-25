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
