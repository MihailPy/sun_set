# pyright: reportUnknownMemberType=false
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMenuBar,
    QPushButton,
    QStatusBar,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from sun_set.api.file_manager import load_from_json, save_to_json
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

        self.file_path = None

        self.btn_choose_file = QAction("Открыть файл", self)
        self.btn_choose_file.setToolTip("Открыть файл с городами")
        self.btn_choose_file.setShortcut(QKeySequence("Ctrl+O"))
        self.btn_choose_file.triggered.connect(self.open_file_dialog)

        self.btn_save_file = QAction("Сохранить файл", self)
        self.btn_save_file.setStatusTip("Сохранить файл с городами")
        self.btn_save_file.setShortcut(QKeySequence("Ctrl+S"))
        self.btn_save_file.triggered.connect(self.save_file)

        self.btn_save_file_as = QAction("Сохранить файл как...", self)
        self.btn_save_file_as.setToolTip("Сохранить города в новый файл")
        self.btn_save_file_as.setShortcut(QKeySequence("Shift+Ctrl+S"))
        self.btn_save_file_as.triggered.connect(self.save_file_as)

        self.setStatusBar(QStatusBar(self))

        menu = QMenuBar(self)
        self.setMenuBar(menu)

        file_menu = menu.addMenu("&Файл")
        if file_menu:
            file_menu.addAction(self.btn_choose_file)
            file_menu.addAction(self.btn_save_file)
            file_menu.addAction(self.btn_save_file_as)

        self.btn_add_city = QPushButton("Добавить город")
        self.btn_add_city.setToolTip("Добавить город в таблицу")
        self.btn_add_city.clicked.connect(self.add_city_in_table)
        self.main_layout.addWidget(self.btn_add_city)

        self.btn_del_city = QPushButton("Удалить города")
        self.btn_del_city.setToolTip("Удалить выбранные города")
        self.btn_del_city.clicked.connect(self.delete_selected_cities)
        self.main_layout.addWidget(self.btn_del_city)

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
        # Вызываем окно выбора файла
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите файл",
            "",
            "JSON Files (*.json)",
        )

        if not file_path:
            return

        result, error = load_from_json(file_path)
        if error != None:
            dlg = CustomDialog(error)
            if dlg.exec():
                self.open_file_dialog()
            return

        if result != None:
            self.file_path = file_path
            self.cities = result

            self.hello_label.hide()

            self.model = CityTableModel(self.cities)
            self.table_view.setModel(self.model)
            self.table_view.show()

            self.table_view.resizeColumnsToContents()

    def save_file(self):
        if not self.file_path:
            self.save_file_as()
        else:
            save_to_json(self.cities, self.file_path)

    def save_file_as(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить файл как...", "", "JSON Files (*.json)"
        )
        if file_path:
            save_to_json(self.cities, file_path)
            self.file_path = file_path

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
