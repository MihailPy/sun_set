from pathlib import Path
from typing import cast

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import QSettings, QTimer
from PyQt6.QtGui import (
    QAction,
    QCloseEvent,
    QKeySequence,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from sun_set.image_export.errors import ExportSettingsError, get_user_friendly_error
from sun_set.image_export.service import build_city_image_preview_from_settings
from sun_set.image_export.settings import (
    ExportImageSettings,
    create_default_export_settings,
    load_export_settings,
    load_month_positions,
    save_export_settings,
    save_month_positions,
)
from sun_set.services.dialog_service import (
    ask_confirmation,
    ask_save_discard_cancel,
    choose_color,
    choose_file,
    choose_save_file,
    show_error,
    show_information,
)

PREVIEW_SCALE_SETTINGS_KEY = "image_export/preview_scale"
SELECTED_MONTH_SETTINGS_KEY = "image_export/selected_month"
MONTH_NAMES = (
    "Январь",
    "Февраль",
    "Март",
    "Апрель",
    "Май",
    "Июнь",
    "Июль",
    "Август",
    "Сентябрь",
    "Октябрь",
    "Ноябрь",
    "Декабрь",
)


def fill_month_combo(combo: QComboBox) -> None:
    for month, month_name in enumerate(
        MONTH_NAMES,
        start=1,
    ):
        combo.addItem(month_name, month)


class ImageExportSettingsDialog(QDialog):
    WINDOW_TITLE = "Настройки экспорта изображения"

    def __init__(
        self,
        settings: ExportImageSettings,
        settings_path: Path | None = None,
        city=None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.settings = settings
        self.settings_path = settings_path

        self.settings_path_edit = QLineEdit()
        self.settings_path_edit.setReadOnly(True)
        self.update_settings_path_field()

        self.city = city
        self.is_dirty = False

        self.update_window_title()
        self.resize(1200, 800)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(settings.image.width)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(settings.image.height)

        self.background_color_edit = QLineEdit(settings.image.background_color)

        self.background_color_button = QPushButton("Выбрать...")
        self.background_color_button.clicked.connect(self.select_background_color)

        self.template_path_edit = QLineEdit(settings.image.template_path or "")

        self.font_path_edit = QLineEdit(settings.text.font_path or "")

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(1, 500)
        self.font_size_spin.setValue(settings.text.font_size)

        self.text_color_edit = QLineEdit(settings.text.color)

        self.text_color_button = QPushButton("Выбрать...")
        self.text_color_button.clicked.connect(self.select_text_color)

        self.row_height_spin = QSpinBox()
        self.row_height_spin.setRange(1, 1000)
        self.row_height_spin.setValue(settings.layout.row_height)

        self.first_column_offset_x_spin = QSpinBox()
        self.first_column_offset_x_spin.setRange(-10000, 10000)
        self.first_column_offset_x_spin.setValue(settings.layout.first_column_offset_x)

        self.second_column_offset_x_spin = QSpinBox()
        self.second_column_offset_x_spin.setRange(-10000, 10000)
        self.second_column_offset_x_spin.setValue(
            settings.layout.second_column_offset_x
        )

        self.month_combo = QComboBox()
        fill_month_combo(self.month_combo)
        self.load_selected_month()

        self.month_x_spin = QSpinBox()
        self.month_x_spin.setRange(-10000, 10000)

        self.month_y_spin = QSpinBox()
        self.month_y_spin.setRange(-10000, 10000)

        self.month_combo.currentIndexChanged.connect(self.load_selected_month_position)
        self.month_combo.currentIndexChanged.connect(self.save_selected_month)
        self.month_x_spin.valueChanged.connect(self.update_selected_month_position)
        self.month_y_spin.valueChanged.connect(self.update_selected_month_position)

        self.shift_x_spin = QSpinBox()
        self.shift_x_spin.setRange(-10000, 10000)
        self.shift_x_spin.setValue(0)

        self.shift_y_spin = QSpinBox()
        self.shift_y_spin.setRange(-10000, 10000)
        self.shift_y_spin.setValue(0)

        self.shift_all_button = QPushButton("Сдвинуть все месяцы")
        self.shift_all_button.clicked.connect(self.shift_all_months)

        self.copy_source_month_combo = QComboBox()
        self.copy_target_month_combo = QComboBox()

        fill_month_combo(self.copy_source_month_combo)
        fill_month_combo(self.copy_target_month_combo)

        self.copy_month_position_button = QPushButton("Копировать координаты месяца")
        self.copy_month_position_button.clicked.connect(self.copy_month_position)

        self.import_month_positions_button = QPushButton("Импортировать координаты")
        self.export_month_positions_button = QPushButton("Экспортировать координаты")

        self.import_month_positions_button.clicked.connect(self.import_month_positions)
        self.export_month_positions_button.clicked.connect(self.export_month_positions)

        self.load_selected_month_position()

        background_color_layout = QHBoxLayout()
        background_color_layout.addWidget(self.background_color_edit)
        background_color_layout.addWidget(self.background_color_button)

        text_color_layout = QHBoxLayout()
        text_color_layout.addWidget(self.text_color_edit)
        text_color_layout.addWidget(self.text_color_button)

        form_layout = QFormLayout()
        form_layout.addRow("Файл настроек:", self.settings_path_edit)
        form_layout.addRow("Ширина:", self.width_spin)
        form_layout.addRow("Высота:", self.height_spin)
        form_layout.addRow(
            "Цвет фона:",
            background_color_layout,
        )
        self.template_path_button = QPushButton("Выбрать...")
        self.template_path_button.clicked.connect(self.select_template_path)

        template_path_layout = QHBoxLayout()
        template_path_layout.addWidget(self.template_path_edit)
        template_path_layout.addWidget(self.template_path_button)

        self.font_path_button = QPushButton("Выбрать...")
        self.font_path_button.clicked.connect(self.select_font_path)

        font_path_layout = QHBoxLayout()
        font_path_layout.addWidget(self.font_path_edit)
        font_path_layout.addWidget(self.font_path_button)

        form_layout.addRow("Шаблон:", template_path_layout)
        form_layout.addRow("Шрифт:", font_path_layout)
        form_layout.addRow("Размер шрифта:", self.font_size_spin)
        form_layout.addRow(
            "Цвет текста:",
            text_color_layout,
        )
        form_layout.addRow("Высота строки:", self.row_height_spin)
        form_layout.addRow(
            "Смещение первой колонки X:", self.first_column_offset_x_spin
        )
        form_layout.addRow(
            "Смещение второй колонки X:", self.second_column_offset_x_spin
        )

        form_layout.addRow("Копировать из месяца:", self.copy_source_month_combo)
        form_layout.addRow("Копировать в месяц:", self.copy_target_month_combo)
        form_layout.addRow("", self.copy_month_position_button)

        form_layout.addRow("Сдвиг X:", self.shift_x_spin)
        form_layout.addRow("Сдвиг Y:", self.shift_y_spin)
        form_layout.addRow("", self.shift_all_button)

        form_layout.addRow("Месяц:", self.month_combo)
        form_layout.addRow("X месяца:", self.month_x_spin)
        form_layout.addRow("Y месяца:", self.month_y_spin)

        form_layout.addRow(
            "",
            self.import_month_positions_button,
        )
        form_layout.addRow(
            "",
            self.export_month_positions_button,
        )

        self.button_box = QDialogButtonBox()
        self.save_button = cast(
            QPushButton,
            self.button_box.addButton(
                "Сохранить", QDialogButtonBox.ButtonRole.AcceptRole
            ),
        )
        self.preview_button = cast(
            QPushButton,
            self.button_box.addButton(
                "Обновить предпросмотр",
                QDialogButtonBox.ButtonRole.ActionRole,
            ),
        )
        self.preview_button.clicked.connect(self.update_preview)
        self.save_as_button = cast(
            QPushButton,
            self.button_box.addButton(
                "Сохранить как",
                QDialogButtonBox.ButtonRole.ActionRole,
            ),
        )
        self.reload_button = cast(
            QPushButton,
            self.button_box.addButton(
                "Перезагрузить",
                QDialogButtonBox.ButtonRole.ActionRole,
            ),
        )
        self.reset_button = cast(
            QPushButton,
            self.button_box.addButton(
                "Сбросить",
                QDialogButtonBox.ButtonRole.ResetRole,
            ),
        )
        self.close_button = cast(
            QPushButton,
            self.button_box.addButton(
                "Закрыть", QDialogButtonBox.ButtonRole.RejectRole
            ),
        )

        self.update_reload_button_state()

        self.save_button.clicked.connect(self.save_settings)
        self.save_as_button.clicked.connect(self.save_settings_as)
        self.reload_button.clicked.connect(self.reload_settings_from_file)
        self.reset_button.clicked.connect(self.reset_settings)
        self.close_button.clicked.connect(self.close)

        self.preview_label = QLabel()
        self.preview_label.setScaledContents(False)

        self.preview_scroll_area = QScrollArea()
        self.preview_scroll_area.setWidget(self.preview_label)
        self.preview_scroll_area.setWidgetResizable(False)

        self.preview_error_label = QLabel()
        self.preview_error_label.setWordWrap(True)

        self.preview_scale_combo = QComboBox()
        self.preview_scale_combo.addItem("По ширине", "fit_width")
        self.preview_scale_combo.addItem("50%", 0.5)
        self.preview_scale_combo.addItem("75%", 0.75)
        self.preview_scale_combo.addItem("100%", 1.0)
        self.preview_scale_combo.addItem("125%", 1.25)
        self.preview_scale_combo.addItem("150%", 1.5)
        self.load_preview_scale()
        self.preview_scale_combo.currentIndexChanged.connect(self.save_preview_scale)
        self.preview_scale_combo.currentIndexChanged.connect(
            self.refresh_preview_pixmap
        )

        self.current_preview_image = None

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.preview_scale_combo)
        left_layout.addWidget(self.preview_scroll_area)
        left_layout.addWidget(self.preview_error_label)

        right_layout = QVBoxLayout()
        right_layout.addLayout(form_layout)
        right_layout.addWidget(self.button_box)

        main_layout = QHBoxLayout(self)
        main_layout.addLayout(left_layout, stretch=3)
        main_layout.addLayout(right_layout, stretch=1)

        self.preview_update_timer = QTimer(self)
        self.preview_update_timer.setSingleShot(True)
        self.preview_update_timer.setInterval(300)
        self.preview_update_timer.timeout.connect(self.update_preview)

        self.width_spin.valueChanged.connect(self.schedule_preview_update)
        self.height_spin.valueChanged.connect(self.schedule_preview_update)
        self.background_color_edit.textChanged.connect(self.schedule_preview_update)
        self.template_path_edit.textChanged.connect(self.schedule_preview_update)
        self.font_path_edit.textChanged.connect(self.schedule_preview_update)
        self.font_size_spin.valueChanged.connect(self.schedule_preview_update)
        self.text_color_edit.textChanged.connect(self.schedule_preview_update)

        self.row_height_spin.valueChanged.connect(self.schedule_preview_update)
        self.first_column_offset_x_spin.valueChanged.connect(
            self.schedule_preview_update
        )
        self.second_column_offset_x_spin.valueChanged.connect(
            self.schedule_preview_update
        )

        self.month_x_spin.valueChanged.connect(self.schedule_preview_update)
        self.month_y_spin.valueChanged.connect(self.schedule_preview_update)

        self.width_spin.valueChanged.connect(self.mark_dirty)
        self.height_spin.valueChanged.connect(self.mark_dirty)
        self.background_color_edit.textChanged.connect(self.mark_dirty)
        self.template_path_edit.textChanged.connect(self.mark_dirty)
        self.font_path_edit.textChanged.connect(self.mark_dirty)
        self.font_size_spin.valueChanged.connect(self.mark_dirty)
        self.text_color_edit.textChanged.connect(self.mark_dirty)

        self.row_height_spin.valueChanged.connect(self.mark_dirty)
        self.first_column_offset_x_spin.valueChanged.connect(self.mark_dirty)
        self.second_column_offset_x_spin.valueChanged.connect(self.mark_dirty)

        self.month_x_spin.valueChanged.connect(self.mark_dirty)
        self.month_y_spin.valueChanged.connect(self.mark_dirty)

        self.update_preview()

        self.setup_shortcuts()

        self.update_reload_button_state()

    def get_selected_month(self) -> int:
        return int(self.month_combo.currentData())

    def update_window_title(self) -> None:
        suffix = " *" if self.is_dirty else ""
        self.setWindowTitle(f"{self.WINDOW_TITLE}{suffix}")

    def mark_dirty(self) -> None:
        if self.is_dirty:
            return

        self.is_dirty = True
        self.update_window_title()

    def mark_clean(self) -> None:
        if not self.is_dirty:
            return

        self.is_dirty = False
        self.update_window_title()

    def load_selected_month_position(self) -> None:
        month = self.get_selected_month()
        month_block = self.settings.layout.month_blocks[month]

        self.month_x_spin.blockSignals(True)
        self.month_y_spin.blockSignals(True)

        self.month_x_spin.setValue(month_block.x)
        self.month_y_spin.setValue(month_block.y)

        self.month_x_spin.blockSignals(False)
        self.month_y_spin.blockSignals(False)

    def update_selected_month_position(self) -> None:
        month = self.get_selected_month()
        month_block = self.settings.layout.month_blocks[month]

        month_block.x = self.month_x_spin.value()
        month_block.y = self.month_y_spin.value()

    def select_template_path(self) -> None:
        file_path = choose_file(
            self,
            "Выберите шаблон изображения",
            "Images (*.png *.jpg *.jpeg)",
            self.template_path_edit.text(),
        )

        if not file_path:
            return

        self.template_path_edit.setText(file_path)
        self.settings.image.template_path = file_path

        self.schedule_preview_update()

    def select_font_path(self) -> None:
        file_path = choose_file(
            self,
            "Выберите шрифт",
            "Fonts (*.ttf *.otf)",
            self.font_path_edit.text(),
        )

        if not file_path:
            return

        self.font_path_edit.setText(file_path)
        self.settings.text.font_path = file_path

        self.schedule_preview_update()

    def update_settings_from_fields(self) -> None:
        self.settings.image.width = self.width_spin.value()
        self.settings.image.height = self.height_spin.value()
        self.settings.image.background_color = self.background_color_edit.text()
        self.settings.image.template_path = self.template_path_edit.text() or None

        self.settings.text.font_path = self.font_path_edit.text() or None
        self.settings.text.font_size = self.font_size_spin.value()
        self.settings.text.color = self.text_color_edit.text()

        self.settings.layout.row_height = self.row_height_spin.value()
        self.settings.layout.first_column_offset_x = (
            self.first_column_offset_x_spin.value()
        )
        self.settings.layout.second_column_offset_x = (
            self.second_column_offset_x_spin.value()
        )

    def save_settings(self) -> bool:
        if self.settings_path is None:
            return self.save_settings_as()

        self.update_settings_from_fields()

        try:
            save_export_settings(self.settings, self.settings_path)
        except ExportSettingsError as error:
            show_error(
                self,
                "Ошибка сохранения настроек",
                get_user_friendly_error(error),
            )
            return False
        except Exception as error:
            show_error(
                self,
                "Ошибка сохранения настроек",
                str(error),
            )
            return False

        self.mark_clean()

        show_information(
            self,
            "Сохранение настроек",
            "Настройки сохранены.",
        )
        return True

    def save_settings_as(self) -> bool:
        start_path = ""

        if self.settings_path is not None:
            start_path = str(self.settings_path)

        settings_file = choose_save_file(
            self,
            "Сохранить настройки экспорта как",
            "JSON files (*.json)",
            start_path,
        )

        if not settings_file:
            return False

        path = Path(settings_file)

        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")

        previous_path = self.settings_path
        self.settings_path = path

        if not self.save_settings():
            self.settings_path = previous_path
            self.update_settings_path_field()
            self.update_reload_button_state()
            return False

        self.update_settings_path_field()
        self.update_reload_button_state()
        return True

    def shift_all_months(self) -> None:
        dx = self.shift_x_spin.value()
        dy = self.shift_y_spin.value()

        if dx == 0 and dy == 0:
            return

        for month_block in self.settings.layout.month_blocks.values():
            month_block.x += dx
            month_block.y += dy

        self.mark_dirty()

        self.load_selected_month_position()

        self.shift_x_spin.setValue(0)
        self.shift_y_spin.setValue(0)

        self.schedule_preview_update()

    def copy_month_position(self) -> None:
        source_month = int(self.copy_source_month_combo.currentData())
        target_month = int(self.copy_target_month_combo.currentData())

        if source_month == target_month:
            return

        source_block = self.settings.layout.month_blocks[source_month]
        target_block = self.settings.layout.month_blocks[target_month]

        target_block.x = source_block.x
        target_block.y = source_block.y

        self.mark_dirty()

        self.schedule_preview_update()

        if self.get_selected_month() == target_month:
            self.load_selected_month_position()

    def save_to_path(self, path: Path) -> None:
        self.update_settings_from_fields()
        save_export_settings(self.settings, path)

        self.settings_path = path
        self.update_settings_path_field()
        self.update_reload_button_state()
        self.mark_clean()

    def set_preview_image(self, image: Image.Image) -> None:
        self.current_preview_image = image
        self.refresh_preview_pixmap()

    def update_preview(self) -> None:
        if self.city is None:
            self.preview_label.setText("Выберите город для предпросмотра.")
            self.preview_error_label.clear()
            self.current_preview_image = None
            return

        self.update_settings_from_fields()

        try:
            image = build_city_image_preview_from_settings(
                city=self.city,
                settings=self.settings,
            )
        except Exception as error:
            self.current_preview_image = None
            self.preview_label.clear()
            self.preview_error_label.setText(
                f"Ошибка предпросмотра: {get_user_friendly_error(error)}"
            )
            return

        self.preview_error_label.clear()
        self.set_preview_image(image)

    def schedule_preview_update(self) -> None:
        self.preview_update_timer.start()

    def refresh_preview_pixmap(self) -> None:
        if self.current_preview_image is None:
            return

        image_qt = ImageQt(self.current_preview_image)
        pixmap = QPixmap.fromImage(image_qt)

        scale_data = self.preview_scale_combo.currentData()

        if scale_data == "fit_width":
            viewport = self.preview_scroll_area.viewport()

            if viewport is None:
                return

            viewport_width = viewport.width()

            if viewport_width > 0 and pixmap.width() > 0:
                target_width = max(viewport_width - 20, 1)
                scale = target_width / pixmap.width()

                pixmap = pixmap.scaled(
                    int(pixmap.width() * scale),
                    int(pixmap.height() * scale),
                )
        else:
            scale = float(scale_data)

            if scale != 1.0:
                pixmap = pixmap.scaled(
                    int(pixmap.width() * scale),
                    int(pixmap.height() * scale),
                )

        self.preview_label.setPixmap(pixmap)
        self.preview_label.resize(pixmap.size())

    def confirm_close(self) -> bool:
        if not self.is_dirty:
            return True

        result = ask_save_discard_cancel(
            self,
            "Несохранённые изменения",
            "Настройки экспорта были изменены. Сохранить изменения?",
        )

        if result == QMessageBox.StandardButton.Save:
            return self.save_settings()

        if result == QMessageBox.StandardButton.Discard:
            return True

        return False

    def closeEvent(self, a0: QCloseEvent | None) -> None:
        if a0 is None:
            return

        if self.confirm_close():
            a0.accept()
        else:
            a0.ignore()

    def update_settings_path_field(self) -> None:
        if self.settings_path is None:
            self.settings_path_edit.setText("Файл не выбран")
            self.settings_path_edit.setToolTip("")
            return

        path_text = str(self.settings_path)
        self.settings_path_edit.setText(path_text)
        self.settings_path_edit.setToolTip(path_text)

    def load_preview_scale(self) -> None:
        settings = QSettings()
        saved_scale = settings.value(
            PREVIEW_SCALE_SETTINGS_KEY,
            "fit_width",
        )

        index = self.preview_scale_combo.findData(saved_scale)

        if index == -1:
            index = self.preview_scale_combo.findData("fit_width")

        self.preview_scale_combo.setCurrentIndex(index)

    def save_preview_scale(self) -> None:
        settings = QSettings()
        settings.setValue(
            PREVIEW_SCALE_SETTINGS_KEY,
            self.preview_scale_combo.currentData(),
        )

    def load_settings_into_fields(self) -> None:
        self.width_spin.setValue(self.settings.image.width)
        self.height_spin.setValue(self.settings.image.height)
        self.background_color_edit.setText(self.settings.image.background_color)
        self.template_path_edit.setText(self.settings.image.template_path or "")

        self.font_path_edit.setText(self.settings.text.font_path or "")
        self.font_size_spin.setValue(self.settings.text.font_size)
        self.text_color_edit.setText(self.settings.text.color)

        self.row_height_spin.setValue(self.settings.layout.row_height)
        self.first_column_offset_x_spin.setValue(
            self.settings.layout.first_column_offset_x
        )
        self.second_column_offset_x_spin.setValue(
            self.settings.layout.second_column_offset_x
        )

        self.load_selected_month_position()

    def reset_settings(self) -> None:
        confirmed = ask_confirmation(
            self,
            "Сброс настроек",
            "Вернуть все настройки экспорта к значениям по умолчанию?",
        )

        if not confirmed:
            return

        defaults = create_default_export_settings()

        self.settings.image = defaults.image
        self.settings.text = defaults.text
        self.settings.layout = defaults.layout

        self.load_settings_into_fields()
        self.mark_dirty()
        self.schedule_preview_update()

    def export_month_positions(self) -> None:
        selected_file = choose_save_file(
            self,
            "Экспортировать координаты месяцев",
            "JSON files (*.json)",
        )

        if not selected_file:
            return

        path = Path(selected_file)

        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")

        try:
            save_month_positions(
                self.settings.layout.month_blocks,
                path,
            )
        except ExportSettingsError as error:
            show_error(
                self,
                "Ошибка экспорта координат",
                get_user_friendly_error(error),
            )
            return
        except Exception as error:
            show_error(
                self,
                "Ошибка экспорта координат",
                str(error),
            )
            return

        show_information(
            self,
            "Экспорт координат",
            "Координаты месяцев экспортированы.",
        )

    def import_month_positions(self) -> None:
        selected_file = choose_file(
            self,
            "Импортировать координаты месяцев",
            "JSON files (*.json)",
        )

        if not selected_file:
            return

        try:
            month_blocks = load_month_positions(Path(selected_file))
        except ExportSettingsError as error:
            show_error(
                self,
                "Ошибка импорта координат",
                get_user_friendly_error(error),
            )
            return
        except Exception as error:
            show_error(
                self,
                "Ошибка импорта координат",
                str(error),
            )
            return

        self.settings.layout.month_blocks = month_blocks

        self.load_selected_month_position()
        self.mark_dirty()
        self.schedule_preview_update()

    def load_selected_month(self) -> None:
        settings = QSettings()
        saved_month = settings.value(
            SELECTED_MONTH_SETTINGS_KEY,
            1,
            type=int,
        )

        index = self.month_combo.findData(saved_month)

        if index == -1:
            index = self.month_combo.findData(1)

        self.month_combo.setCurrentIndex(index)

    def save_selected_month(self) -> None:
        settings = QSettings()
        settings.setValue(
            SELECTED_MONTH_SETTINGS_KEY,
            self.get_selected_month(),
        )

    def update_reload_button_state(self) -> None:
        is_available = self.settings_path is not None

        self.reload_button.setEnabled(is_available)

        if hasattr(self, "reload_action"):
            self.reload_action.setEnabled(is_available)

    def reload_settings_from_file(self) -> None:
        if self.settings_path is None:
            return

        if self.is_dirty:
            confirmed = ask_confirmation(
                self,
                "Перезагрузка настроек",
                (
                    "Несохранённые изменения будут потеряны. "
                    "Перезагрузить настройки из файла?"
                ),
            )

            if not confirmed:
                return

        try:
            loaded_settings = load_export_settings(self.settings_path)
        except ExportSettingsError as error:
            show_error(
                self,
                "Ошибка загрузки настроек",
                get_user_friendly_error(error),
            )
            return
        except Exception as error:
            show_error(
                self,
                "Ошибка загрузки настроек",
                str(error),
            )
            return

        self.settings.image = loaded_settings.image
        self.settings.text = loaded_settings.text
        self.settings.layout = loaded_settings.layout

        self.load_settings_into_fields()
        self.mark_clean()
        self.schedule_preview_update()

    def setup_shortcuts(self) -> None:
        self.save_action = QAction(self)
        self.save_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_action.triggered.connect(self.save_settings)
        self.addAction(self.save_action)

        self.save_as_action = QAction(self)
        self.save_as_action.setShortcut(QKeySequence.StandardKey.SaveAs)
        self.save_as_action.triggered.connect(self.save_settings_as)
        self.addAction(self.save_as_action)

        self.refresh_preview_action = QAction(self)
        self.refresh_preview_action.setShortcut(QKeySequence.StandardKey.Refresh)
        self.refresh_preview_action.triggered.connect(self.update_preview)
        self.addAction(self.refresh_preview_action)

        self.reload_action = QAction(self)
        self.reload_action.setShortcut(QKeySequence("Ctrl+R"))
        self.reload_action.triggered.connect(self.reload_settings_from_file)
        self.addAction(self.reload_action)

        self.reset_action = QAction(self)
        self.reset_action.setShortcut(QKeySequence("Ctrl+0"))
        self.reset_action.triggered.connect(self.reset_settings)
        self.addAction(self.reset_action)

        self.save_button.setToolTip("Сохранить настройки (Ctrl+S)")

        self.save_as_button.setToolTip(
            "Сохранить настройки в другой файл (Ctrl+Shift+S)"
        )
        self.preview_button.setToolTip("Обновить предпросмотр (F5)")
        self.reload_button.setToolTip("Перезагрузить настройки из файла (Ctrl+R)")
        self.reset_button.setToolTip("Вернуть настройки по умолчанию (Ctrl+0)")

    def select_background_color(self) -> None:
        color = choose_color(
            self,
            "Выберите цвет фона",
            self.background_color_edit.text(),
        )

        if color is None:
            return

        self.background_color_edit.setText(color)

    def select_text_color(self) -> None:
        color = choose_color(
            self,
            "Выберите цвет текста",
            self.text_color_edit.text(),
        )

        if color is None:
            return

        self.text_color_edit.setText(color)
