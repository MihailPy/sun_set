# pyright: reportUnknownMemberType=false
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
)

from sun_set.api.file_manager import load_from_json


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sun set")
        self.resize(300, 200)

        self.widget = QLabel("Hello")
        font = self.widget.font()
        font.setPointSize(30)
        self.widget.setFont(font)
        self.widget.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )

        self.setCentralWidget(self.widget)

        # Кнопка выбора файла, для импорта городов
        self.btn_choose_file = QPushButton("Выбрать файл", self)
        self.btn_choose_file.setToolTip("Импортировать города из файла")
        self.btn_choose_file.setGeometry(10, 10, 110, 40)
        self.btn_choose_file.clicked.connect(self.open_file_dialog)

    def open_file_dialog(self):
        while True:
            # Вызываем окно выбора файла
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Выберите файл",
                "",
                "Текстовые файлы (*.json)",
            )

            if not file_path:
                break

            if file_path:
                self.cities = load_from_json(file_path)
                print(f"{self.cities}")
                if isinstance(self.cities, str):
                    dlg = CustomDialog(self.cities)
                    if dlg.exec():
                        continue
                    else:
                        break
                else:
                    break


class CustomDialog(QDialog):
    def __init__(self, error_msg: str):
        super().__init__()

        self.setWindowTitle("Ошибка")

        QBtn = (
            QDialogButtonBox.StandardButton.Retry
            | QDialogButtonBox.StandardButton.Cancel
        )

        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.main_layout = QVBoxLayout()
        error_label = QLabel(error_msg)
        error_label.setStyleSheet("color: red;")
        message = QLabel("Выбрать файл снова?")
        self.main_layout.addWidget(error_label)
        self.main_layout.addWidget(message)
        self.main_layout.addWidget(self.buttonBox)
        self.setLayout(self.main_layout)
