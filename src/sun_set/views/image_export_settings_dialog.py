from pathlib import Path
from typing import cast

from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
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
from sun_set.image_export.settings import ExportImageSettings, save_export_settings


class ImageExportSettingsDialog(QDialog):
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
        self.city = city

        self.setWindowTitle("Настройки экспорта изображения")
        self.resize(1200, 800)

        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 10000)
        self.width_spin.setValue(settings.image.width)

        self.height_spin = QSpinBox()
        self.height_spin.setRange(1, 10000)
        self.height_spin.setValue(settings.image.height)

        self.background_color_edit = QLineEdit(settings.image.background_color)
        self.template_path_edit = QLineEdit(settings.image.template_path or "")

        self.font_path_edit = QLineEdit(settings.text.font_path or "")

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(1, 500)
        self.font_size_spin.setValue(settings.text.font_size)

        self.text_color_edit = QLineEdit(settings.text.color)

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
        for month in range(1, 13):
            self.month_combo.addItem(str(month), month)

        self.month_x_spin = QSpinBox()
        self.month_x_spin.setRange(-10000, 10000)

        self.month_y_spin = QSpinBox()
        self.month_y_spin.setRange(-10000, 10000)

        self.month_combo.currentIndexChanged.connect(self.load_selected_month_position)
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

        for month in range(1, 13):
            self.copy_source_month_combo.addItem(str(month), month)
            self.copy_target_month_combo.addItem(str(month), month)

        self.copy_month_position_button = QPushButton("Копировать координаты месяца")
        self.copy_month_position_button.clicked.connect(self.copy_month_position)

        self.load_selected_month_position()

        form_layout = QFormLayout()
        form_layout.addRow("Ширина:", self.width_spin)
        form_layout.addRow("Высота:", self.height_spin)
        form_layout.addRow("Цвет фона:", self.background_color_edit)
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
        form_layout.addRow("Цвет текста:", self.text_color_edit)
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
        self.close_button = cast(
            QPushButton,
            self.button_box.addButton(
                "Закрыть", QDialogButtonBox.ButtonRole.RejectRole
            ),
        )

        self.save_button.clicked.connect(self.save_settings)
        self.save_as_button.clicked.connect(self.save_settings_as)
        self.close_button.clicked.connect(self.reject)

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
        self.preview_scale_combo.setCurrentText("По ширине")
        self.preview_scale_combo.currentIndexChanged.connect(
            self.refresh_preview_pixmap
        )
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

        self.update_preview()

    def get_selected_month(self) -> int:
        return int(self.month_combo.currentData())

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
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите шаблон изображения",
            self.template_path_edit.text(),
            "Images (*.png *.jpg *.jpeg)",
        )

        if not file_path:
            return

        self.template_path_edit.setText(file_path)
        self.settings.image.template_path = file_path

        self.schedule_preview_update()

    def select_font_path(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите шрифт",
            self.font_path_edit.text(),
            "Fonts (*.ttf *.otf)",
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

    def save_settings(self) -> None:
        if self.settings_path is None:
            self.save_settings_as()
            return

        self.update_settings_from_fields()

        try:
            save_export_settings(self.settings, self.settings_path)
        except ExportSettingsError as error:
            QMessageBox.critical(
                self,
                "Ошибка сохранения настроек",
                get_user_friendly_error(error),
            )
            return
        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка сохранения настроек",
                str(error),
            )
            return

        QMessageBox.information(
            self,
            "Сохранение настроек",
            "Настройки сохранены.",
        )

    def save_settings_as(self) -> None:
        start_path = ""

        if self.settings_path is not None:
            start_path = str(self.settings_path)

        settings_file, _ = QFileDialog.getSaveFileName(
            self,
            "Сохранить настройки экспорта как",
            start_path,
            "JSON files (*.json)",
        )

        if not settings_file:
            return

        path = Path(settings_file)

        if path.suffix.lower() != ".json":
            path = path.with_suffix(".json")

        self.settings_path = path
        self.save_settings()

    def shift_all_months(self) -> None:
        dx = self.shift_x_spin.value()
        dy = self.shift_y_spin.value()

        if dx == 0 and dy == 0:
            return

        for month_block in self.settings.layout.month_blocks.values():
            month_block.x += dx
            month_block.y += dy

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

        self.schedule_preview_update()

        if self.get_selected_month() == target_month:
            self.load_selected_month_position()

    def save_to_path(self, path: Path) -> None:
        self.update_settings_from_fields()
        save_export_settings(self.settings, path)
        self.settings_path = path

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
