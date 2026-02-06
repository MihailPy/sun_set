# pyright: reportUnknownMemberType=false
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from sun_set.api.file_manager import load_from_json
from sun_set.models.city import City


class CityTableModel(QAbstractTableModel):
    def __init__(self, cities: list[City]) -> None:
        super().__init__()
        self.cities = cities
        self.headers = ["Город", "Регион", "Широта", "Высота", "Timezone", "Высота ASL"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.cities)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            city = self.cities[index.row()]

            if index.column() == 0:
                return city.name
            if index.column() == 1:
                return city.region
            if index.column() == 2:
                return str(city.lat)
            if index.column() == 3:
                return str(city.lon)
            if index.column() == 4:
                return city.timezone
            if index.column() == 5:
                return str(city.elevation)
        return None

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if (
            role == Qt.ItemDataRole.DisplayRole
            and orientation == Qt.Orientation.Horizontal
        ):
            return self.headers[section]
        return None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sun set")
        self.resize(600, 400)  # Увеличил размер для таблицы

        # 1. Создаем центральный виджет и главный макет
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # 2. Кнопка (лучше добавить её в макет, а не через setGeometry)
        self.btn_choose_file = QPushButton("Выбрать файл")
        self.btn_choose_file.setToolTip("Импортировать города из файла")
        self.btn_choose_file.clicked.connect(self.open_file_dialog)
        self.main_layout.addWidget(self.btn_choose_file)

        # 3. Приветственная надпись
        self.hello_label = QLabel("Выберите файл для загрузки данных")
        self.hello_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.hello_label)

        # 4. Заготовка под таблицу (пока пустая)
        self.table_view = QTableView()
        self.table_view.hide()  # Прячем, пока нет данных
        self.main_layout.addWidget(self.table_view)

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
        if not isinstance(self.cities, str):
            # Скрываем надпись "Hello"
            self.hello_label.hide()

            # Настраиваем модель и показываем таблицу
            self.model = CityTableModel(self.cities)
            self.table_view.setModel(self.model)
            self.table_view.show()

            # Опционально: растянуть колонки по содержимому
            self.table_view.resizeColumnsToContents()


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
