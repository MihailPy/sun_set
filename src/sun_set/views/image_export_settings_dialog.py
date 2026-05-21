from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from sun_set.image_export.settings import ExportImageSettings


class ImageExportSettingsDialog(QDialog):
    def __init__(
        self,
        settings: ExportImageSettings,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)

        self.settings = settings

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

        form_layout = QFormLayout()
        form_layout.addRow("Ширина:", self.width_spin)
        form_layout.addRow("Высота:", self.height_spin)
        form_layout.addRow("Цвет фона:", self.background_color_edit)
        form_layout.addRow("Шаблон:", self.template_path_edit)
        form_layout.addRow("Шрифт:", self.font_path_edit)
        form_layout.addRow("Размер шрифта:", self.font_size_spin)
        form_layout.addRow("Цвет текста:", self.text_color_edit)
        form_layout.addRow("Высота строки:", self.row_height_spin)
        form_layout.addRow(
            "Смещение первой колонки X:", self.first_column_offset_x_spin
        )
        form_layout.addRow(
            "Смещение второй колонки X:", self.second_column_offset_x_spin
        )

        layout = QVBoxLayout(self)
        layout.addLayout(form_layout)
