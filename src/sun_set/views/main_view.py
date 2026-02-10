# pyright: reportUnknownMemberType=false
from PyQt6.QtCore import Qt
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
from sun_set.models.table_model import CheckBoxHeader, CityTableModel
from sun_set.views.delegates.custom_delegate import CityDelegate


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

        self.btn_add_city = QPushButton("Добавить город")
        self.btn_add_city.setToolTip("Добавить город в таблицу")
        self.btn_add_city.clicked.connect(self.add_city_in_table)
        self.main_layout.addWidget(self.btn_add_city)

        self.btn_del_city = QPushButton("Удалить города")
        self.btn_del_city.setToolTip("Удалить выбранные города")
        self.btn_del_city.clicked.connect(self.delete_selected_cities)
        self.main_layout.addWidget(self.btn_del_city)

        # 3. Приветственная надпись
        self.hello_label = QLabel(
            """Выберите файл для загрузки данных городов, или нажмите 'Добавить город'"""
        )
        self.hello_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.hello_label)

        # 4. Заготовка под таблицу (пока пустая)
        self.table_view = QTableView()
        header = CheckBoxHeader(Qt.Orientation.Horizontal, self.table_view)
        self.table_view.setHorizontalHeader(header)
        self.table_view.hide()  # Прячем, пока нет данных
        self.table_view.setItemDelegate(CityDelegate(self.table_view))
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

    def add_city_in_table(self):
        new_city = City(
            name="Новый город",
            region="-",
            lat=0.0,
            lon=0.0,
            timezone="UTC",
            elevation=0,
        )
        # Если модель еще не была создана (например, при первом нажатии)
        if not hasattr(self, "model") or self.model is None:
            self.cities = [new_city]
            self.model = CityTableModel(self.cities)
            self.table_view.setModel(self.model)
            self.table_view.show()
            self.hello_label.hide()
        else:
            # Если модель уже есть, просто добавляем в неё данные
            self.model.addCity(new_city)
            if len(self.cities) == 1:
                self.hello_label.hide()
                self.table_view.show()

        print(f"{self.cities}")
        self.table_view.resizeColumnsToContents()

    def delete_selected_cities(self):
        if hasattr(self, "model") and self.model is not None:
            self.model.removeCheckedCities()
            self.table_view.resizeColumnsToContents()
            self.cities = self.model.cities
            if len(self.cities) == 0:
                self.table_view.hide()
                header = CheckBoxHeader(Qt.Orientation.Horizontal, self.table_view)
                self.table_view.setHorizontalHeader(header)
                self.hello_label.show()


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
