from pathlib import Path
from typing import cast

from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from sun_set.image_export.errors import ExportSettingsError, get_user_friendly_error
from sun_set.image_export.settings import ExportImageSettings, save_export_settings


class ImageExportSettingsDialog(QDialog):
    def __init__(
        self,
        settings: ExportImageSettings,
        settings_path: Path | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.settings = settings
        self.settings_path = settings_path

        self.setWindowTitle("Настройки экспорта изображения")
        self.resize(500, 400)

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
        form_layout.addRow("Месяц:", self.month_combo)
        form_layout.addRow("X месяца:", self.month_x_spin)
        form_layout.addRow("Y месяца:", self.month_y_spin)

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)

        self.button_box = QDialogButtonBox()
        self.save_button = cast(
            QPushButton,
            self.button_box.addButton(
                "Сохранить", QDialogButtonBox.ButtonRole.AcceptRole
            ),
        )
        self.close_button = cast(
            QPushButton,
            self.button_box.addButton(
                "Закрыть", QDialogButtonBox.ButtonRole.RejectRole
            ),
        )

        self.save_button.clicked.connect(self.save_settings)
        self.close_button.clicked.connect(self.reject)

        layout.addWidget(self.button_box)

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
            QMessageBox.warning(
                self,
                "Сохранение настроек",
                "Путь к файлу настроек не выбран.",
            )
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
