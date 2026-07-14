from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
)

from sun_set.app_info import get_app_version


class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("О программе")
        self.setMinimumWidth(360)

        title_label = QLabel("<h2>Sun Set</h2>")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.version_label = QLabel(f"Версия {get_app_version()}")
        self.version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        description_label = QLabel(
            "Приложение для расчёта, просмотра и экспорта данных о времени заката."
        )
        description_label.setWordWrap(True)
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        author_label = QLabel("Автор: MihailPy")
        author_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        repository_label = QLabel(
            '<a href="https://github.com/MihailPy/sun_set">GitHub проекта</a>'
        )
        repository_label.setOpenExternalLinks(True)
        repository_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(title_label)
        layout.addWidget(self.version_label)
        layout.addSpacing(8)
        layout.addWidget(description_label)
        layout.addWidget(author_label)
        layout.addWidget(repository_label)
        layout.addSpacing(8)
        layout.addWidget(buttons)
