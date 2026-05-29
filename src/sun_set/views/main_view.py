from datetime import datetime
from pathlib import Path

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QAction, QDesktopServices, QKeySequence
from PyQt6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStatusBar,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from sun_set.api.file_manager import load_from_json, save_to_json
from sun_set.core.astronomy import get_city_sunset
from sun_set.image_export.errors import ImageExportError, get_user_friendly_error
from sun_set.image_export.service import build_city_image_preview, export_cities_images
from sun_set.image_export.settings import (
    create_default_export_settings,
    load_export_settings,
)
from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData
from sun_set.models.table_model import (
    STATUS_COLUMN,
    CheckBoxHeader,
    CityTableModel,
    StatusActionDelegate,
)
from sun_set.views.delegates.custom_delegate import CityDelegate
from sun_set.views.image_export_settings_dialog import ImageExportSettingsDialog
from sun_set.views.image_preview_dialog import ImagePreviewDialog
from sun_set.views.sunset_table_view import YearEditorWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sun set")
        self.resize(800, 400)

        self.file_path = None
        self.last_image_export_settings_path: str = ""
        self.last_image_export_output_dir: str = ""

        self.cities: list[City] = []
        self.model: CityTableModel | None = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.setStatusBar(QStatusBar(self))

        self._setup_menu()
        self._setup_city_group()
        self._setup_date_group()

    def _setup_menu(self) -> None:
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

        menu = QMenuBar(self)
        self.setMenuBar(menu)

        file_menu = menu.addMenu("&Файл")
        if file_menu:
            file_menu.addAction(self.btn_choose_file)
            file_menu.addAction(self.btn_save_file)
            file_menu.addAction(self.btn_save_file_as)

    def _setup_city_group(self) -> None:
        city_group = QGroupBox("Города")
        city_group.setSizePolicy(
            QSizePolicy.Policy.Preferred,
            QSizePolicy.Policy.Preferred,
        )

        city_main_layout = QVBoxLayout()

        city_btn_group_layout = QHBoxLayout()
        self._setup_city_buttons(city_btn_group_layout)
        city_main_layout.addLayout(city_btn_group_layout)

        self.initial_prompt_text = QLabel(
            "Выберите файл для загрузки данных городов, или нажмите 'Добавить'"
        )
        self.initial_prompt_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        city_main_layout.addWidget(self.initial_prompt_text)

        self._setup_table()
        city_main_layout.addWidget(self.table_view)

        city_group.setLayout(city_main_layout)
        self.main_layout.addWidget(city_group)

    def _setup_city_buttons(self, layout: QHBoxLayout) -> None:
        self.btn_add_city = QPushButton("Добавить")
        self.btn_add_city.setToolTip("Добавить город в таблицу")
        self.btn_add_city.clicked.connect(self.add_city_in_table)
        layout.addWidget(self.btn_add_city)

        self.btn_del_city = QPushButton("Удалить")
        self.btn_del_city.setToolTip("Удалить выбранные города")
        self.btn_del_city.clicked.connect(self.delete_selected_cities)
        layout.addWidget(self.btn_del_city)

        self.btn_get_sunset_info = QPushButton("Обновить", self)
        self.btn_get_sunset_info.setToolTip("Обновить выбранные данные закатов")
        self.btn_get_sunset_info.clicked.connect(self.initiate_sunset_fetch)
        layout.addWidget(self.btn_get_sunset_info)

        self.btn_export_image = QPushButton("Экспорт", self)
        self.btn_export_image.setToolTip("Экспорт выбранных городов в изображение")
        self.btn_export_image.clicked.connect(self.export_all_selected_city_image)
        layout.addWidget(self.btn_export_image)

        self.preview_image_button = QPushButton("Предпросмотр", self)
        self.preview_image_button.setToolTip(
            "Предпросмотр перед сохранением изображения"
        )
        self.preview_image_button.clicked.connect(self.preview_selected_city_image)
        layout.addWidget(self.preview_image_button)

        self.image_export_settings_button = QPushButton("Настройки экспорта", self)

        image_export_settings_menu = QMenu(self)

        create_settings_action = image_export_settings_menu.addAction(
            "Создать настройки"
        )
        create_settings_action.triggered.connect(self.create_image_export_settings)

        edit_settings_action = image_export_settings_menu.addAction(
            "Редактировать настройки"
        )
        edit_settings_action.triggered.connect(self.edit_image_export_settings)

        self.image_export_settings_button.setMenu(image_export_settings_menu)
        layout.addWidget(self.image_export_settings_button)

        layout.addStretch()

    def _setup_table(self) -> None:
        self.table_view = QTableView()

        header = CheckBoxHeader(Qt.Orientation.Horizontal, self.table_view)
        self.table_view.setHorizontalHeader(header)
        header.setSectionResizeMode(
            STATUS_COLUMN, QHeaderView.ResizeMode.ResizeToContents
        )

        self.table_view.hide()
        self.table_view.setItemDelegate(CityDelegate(self.table_view))

        self.status_delegate = StatusActionDelegate(self.table_view)
        self.table_view.setItemDelegateForColumn(STATUS_COLUMN, self.status_delegate)
        self.status_delegate.buttonClicked.connect(self.handle_city_update)

    def _setup_date_group(self) -> None:
        date_group = QGroupBox("Настройки для сбора данных закатов")
        date_group.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)

        date_group_layout = QHBoxLayout()

        current_year = datetime.now().year
        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(current_year - 50, current_year + 50)
        self.year_spinbox.setValue(current_year + 1)

        date_group_layout.addWidget(QLabel("Год:"))
        date_group_layout.addWidget(self.year_spinbox)

        days = [
            ("Пн", 0),
            ("Вт", 1),
            ("Ср", 2),
            ("Чт", 3),
            ("Пт", 4),
            ("Сб", 5),
            ("Вс", 6),
        ]

        self.combo_weekday1 = QComboBox()
        self.combo_weekday2 = QComboBox()

        for name, value in days:
            self.combo_weekday1.addItem(name, value)
            self.combo_weekday2.addItem(name, value)

        self.combo_weekday1.setCurrentIndex(4)
        self.combo_weekday2.setCurrentIndex(5)

        date_group_layout.addWidget(QLabel("Интересующие дни 1:"))
        date_group_layout.addWidget(self.combo_weekday1)
        date_group_layout.addWidget(QLabel("2:"))
        date_group_layout.addWidget(self.combo_weekday2)

        date_group.setLayout(date_group_layout)
        self.main_layout.addWidget(date_group)

    def setup_city_model(self, cities: list[City]) -> None:
        self.cities = cities
        self.model = CityTableModel(self.cities)
        self.model.dataChanged.connect(self.on_data_changed)
        self.table_view.setModel(self.model)
        self.table_view.show()
        self.initial_prompt_text.hide()
        self.table_view.resizeColumnsToContents()

    def show_no_cities_warning(self) -> None:
        QMessageBox.warning(
            self,
            "Города",
            "Сначала загрузите или создайте города.",
        )

    def on_data_changed(self, top_left, bottom_right, roles):
        if self.model is None:
            self.show_no_cities_warning()
            return

        if hasattr(self, "_updating") and self._updating:
            return

        self._updating = True

        city = self.model.cities[top_left.row()]
        index = self.model.index(top_left.row(), STATUS_COLUMN)

        if city.get_stable_hash() != city.sunset_data.hash_before_edit:
            self.model.status_overrides[index.row()] = "❗️ Неактуальные данные"
            self.model.setData(index, False, StatusActionDelegate.ViewEnabledRole)
            self.model.setData(index, True, StatusActionDelegate.UpdateEnabledRole)
        else:
            if city.sunset_data.source == Source.CALCULATED:
                self.model.status_overrides[index.row()] = "✅ Загружено"
                self.model.setData(index, True, StatusActionDelegate.ViewEnabledRole)
                self.model.setData(index, False, StatusActionDelegate.UpdateEnabledRole)
            elif city.sunset_data.source == Source.EDITED:
                self.model.status_overrides[index.row()] = "⚠️ Изменено"
                self.model.setData(index, True, StatusActionDelegate.ViewEnabledRole)
                self.model.setData(index, True, StatusActionDelegate.UpdateEnabledRole)

        self.table_view.resizeColumnToContents(STATUS_COLUMN)

        self._updating = False

    def handle_city_update(self, row: int, action_type: str):
        if self.model is None:
            self.show_no_cities_warning()
            return

        city = self.model.cities[row]
        if action_type == "view":
            self.extra_window = YearEditorWindow(city)
            self.extra_window.dataChanged.connect(
                lambda: self.on_city_data_changed(row)
            )
            self.extra_window.show()

        if action_type == "update":
            print(f"Запуск обновления для города: {city.name} (строка {row})")
            year = self.year_spinbox.value()
            weekday1 = self.combo_weekday1.currentIndex()
            weekday2 = self.combo_weekday2.currentIndex()

            city.sunset_data = get_city_sunset(city, year, weekday1, weekday2)

            city.sunset_data.hash_before_edit = city.get_stable_hash()

            index = self.model.index(row, STATUS_COLUMN)
            if row in self.model.status_overrides:
                del self.model.status_overrides[row]

            index = self.model.index(row, STATUS_COLUMN)
            self.model.dataChanged.emit(
                index,
                index,
                [
                    Qt.ItemDataRole.DisplayRole,
                    StatusActionDelegate.UpdateEnabledRole,
                    StatusActionDelegate.ViewEnabledRole,
                ],
            )

        self.table_view.resizeColumnToContents(STATUS_COLUMN)

    def on_city_data_changed(self, row: int):
        """Обработчик изменения данных города через окно редактирования"""
        if self.model is None:
            self.show_no_cities_warning()
            return

        # Обновляем hash после редактирования
        city = self.model.cities[row]
        city.sunset_data.hash_before_edit = city.get_stable_hash()

        # Обновляем отображение строки
        self.update_city_row_display(row)

        self.table_view.resizeColumnToContents(STATUS_COLUMN)

    def update_city_row_display(self, row: int):
        """Вспомогательный метод для обновления отображения строки"""
        if self.model is None:
            self.show_no_cities_warning()
            return

        index = self.model.index(row, STATUS_COLUMN)
        self.model.dataChanged.emit(
            index,
            index,
            [
                Qt.ItemDataRole.DisplayRole,
                StatusActionDelegate.UpdateEnabledRole,
                StatusActionDelegate.ViewEnabledRole,
            ],
        )

    def initiate_sunset_fetch(self):
        year = self.year_spinbox.value()
        weekday1 = self.combo_weekday1.currentIndex()
        weekday2 = self.combo_weekday2.currentIndex()
        if hasattr(self, "model") and self.model is not None:
            updated_rows = self.model.update_checked_cities(year, weekday1, weekday2)
            if updated_rows:
                self.table_view.resizeColumnToContents(STATUS_COLUMN)

    def export_all_selected_city_image(self):
        cities = self.get_selected_cities_or_none()

        if cities is None:
            self.show_no_cities_warning()
            return

        settings_file, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите настройки экспорта",
            self.last_image_export_settings_path,
            "JSON files (*.json)",
        )

        if settings_file:
            self.last_image_export_settings_path = settings_file

        if not settings_file:
            return
        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Выберите папку для сохранения изображений",
            self.last_image_export_output_dir,
        )

        if output_dir:
            self.last_image_export_output_dir = output_dir

        if not output_dir:
            return

        results = export_cities_images(
            cities=cities,
            settings_path=Path(settings_file),
            output_dir=Path(output_dir),
        )

        failed_results = [result for result in results if not result.success]
        success_count = sum(result.success for result in results)
        error_count = len(results) - success_count

        message = f"Готово: {success_count}\nОшибки: {error_count}"

        if failed_results:
            errors_text = "\n".join(
                f"- {result.city_name}: {result.error}"
                for result in failed_results[:10]
            )

            message += f"\n\nОшибки:\n{errors_text}"

            if len(failed_results) > 10:
                message += f"\n...и ещё {len(failed_results) - 10}"

        report_path = Path(output_dir) / "image_export_report.txt"
        report_lines = [
            f"Готово: {success_count}",
            f"Ошибки: {error_count}",
            "",
        ]

        for result in results:
            if result.success:
                report_lines.append(f"OK: {result.city_name} -> {result.output_path}")
            else:
                report_lines.append(f"ERROR: {result.city_name} -> {result.error}")

        report_path.write_text("\n".join(report_lines), encoding="utf-8")

        message_box = QMessageBox(self)
        message_box.setWindowTitle("Экспорт изображений")
        message_box.setText(message)
        message_box.setIcon(QMessageBox.Icon.Information)

        open_folder_button = message_box.addButton(
            "Открыть папку",
            QMessageBox.ButtonRole.ActionRole,
        )
        message_box.addButton(QMessageBox.StandardButton.Ok)

        message_box.exec()

        if message_box.clickedButton() == open_folder_button:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(output_dir)))

    def preview_selected_city_image(self) -> None:
        cities = self.get_selected_cities_or_none()
        city = cities[0] if cities else None

        if city is None:
            self.show_no_cities_warning()
            return

        settings_file, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите настройки экспорта",
            self.last_image_export_settings_path,
            "JSON files (*.json)",
        )

        if settings_file:
            self.last_image_export_settings_path = settings_file
        if not settings_file:
            return

        try:
            image = build_city_image_preview(
                city=city,
                settings_path=Path(settings_file),
            )
        except ImageExportError as error:
            QMessageBox.critical(
                self,
                "Ошибка предпросмотра",
                get_user_friendly_error(error),
            )
            return
        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка предпросмотра",
                get_user_friendly_error(error),
            )
            return

        dialog = ImagePreviewDialog(image=image, parent=self)
        dialog.exec()

    def edit_image_export_settings(self) -> None:
        settings_file, _ = QFileDialog.getOpenFileName(
            self,
            "Выберите настройки экспорта",
            self.last_image_export_settings_path,
            "JSON files (*.json)",
        )

        if not settings_file:
            return

        self.last_image_export_settings_path = settings_file

        try:
            settings = load_export_settings(Path(settings_file))
        except ImageExportError as error:
            QMessageBox.critical(
                self,
                "Ошибка настроек экспорта",
                get_user_friendly_error(error),
            )
            return
        except Exception as error:
            QMessageBox.critical(
                self,
                "Ошибка настроек экспорта",
                str(error),
            )
            return

        city = self.get_current_city_or_none()

        dialog = ImageExportSettingsDialog(
            settings=settings,
            settings_path=Path(settings_file),
            city=city,
            parent=self,
        )
        dialog.exec()

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
        if error is not None:
            retry = QMessageBox.question(
                self,
                "Ошибка",
                f"{error}\n\nВыбрать файл снова?",
                QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Retry,
            )

            if retry == QMessageBox.StandardButton.Retry:
                self.open_file_dialog()

            return

        if result is not None:
            self.file_path = file_path
            self.setup_city_model(result)

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
            sunset_data=YearData(
                year=self.year_spinbox.value(),
                source=Source.CALCULATED,
                hash_before_edit=None,
                months=None,
            ),
        )
        # Если модель еще не была создана (например, при первом нажатии)
        if not hasattr(self, "model") or self.model is None:
            self.setup_city_model([new_city])
        else:
            # Если модель уже есть, просто добавляем в неё данные
            self.model.add_city(new_city)
            if len(self.cities) == 1:
                self.initial_prompt_text.hide()
                self.table_view.show()

        self.table_view.resizeColumnsToContents()

    def delete_selected_cities(self):
        if hasattr(self, "model") and self.model is not None:
            self.model.remove_checked_cities()
            self.table_view.resizeColumnsToContents()
            self.cities = self.model.cities
            if len(self.cities) == 0:
                self.table_view.hide()
                header = CheckBoxHeader(Qt.Orientation.Horizontal, self.table_view)
                self.table_view.setHorizontalHeader(header)
                self.initial_prompt_text.show()

    def create_image_export_settings(self) -> None:
        settings = create_default_export_settings()
        city = self.get_current_city_or_none()

        dialog = ImageExportSettingsDialog(
            settings=settings,
            settings_path=None,
            city=city,
            parent=self,
        )
        dialog.exec()

    def get_current_city_or_none(self) -> City | None:
        if self.model is None:
            return None

        cities = self.model.get_selected_city()
        if not cities:
            return None

        return cities[0]

    def get_selected_cities_or_none(self) -> list[City] | None:
        if self.model is None:
            self.show_no_cities_warning()
            return None

        cities = self.model.get_selected_city()
        if not cities:
            return None

        return cities
