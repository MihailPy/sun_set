from datetime import datetime
from pathlib import Path

from PIL import Image
from PyQt6.QtCore import QModelIndex, Qt
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QStatusBar,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from sun_set.image_export.errors import ImageExportError, get_user_friendly_error
from sun_set.image_export.service import (
    ExportResult,
    build_city_image_preview,
    build_export_summary_message,
    export_cities_images,
    save_export_report,
)
from sun_set.image_export.settings import (
    create_default_export_settings,
    load_export_settings,
)
from sun_set.models.city import City
from sun_set.models.table_model import (
    STATUS_COLUMN,
    CheckBoxHeader,
    CityTableModel,
    StatusActionDelegate,
)
from sun_set.services.city_file_service import (
    load_cities_from_file,
    save_cities_to_file,
)
from sun_set.services.city_service import (
    create_default_city,
    update_cities_sunset,
    update_city_sunset,
)
from sun_set.services.dialog_service import (
    ask_open_folder_after_export,
    ask_retry,
    choose_directory,
    choose_file,
    choose_save_file,
    open_directory,
    show_error,
    show_warning,
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

        self.file_path: str | None = None
        self.last_image_export_settings_path: str = ""
        self.last_image_export_output_dir: str = ""

        self.cities: list[City] = []
        self.model: CityTableModel | None = None

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

        self._setup_menu()
        self._setup_date_group()
        self._setup_city_group()

        self.update_window_title()

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
        city_group = QWidget()

        city_main_layout = QVBoxLayout()

        actions_layout = QHBoxLayout()

        city_actions_group = QGroupBox("Города")
        city_actions_layout = QHBoxLayout()
        self._setup_city_buttons(city_actions_layout)
        city_actions_group.setLayout(city_actions_layout)
        city_actions_group.setMaximumHeight(city_actions_group.sizeHint().height())

        export_actions_group = QGroupBox("Изображения")

        export_actions_layout = QVBoxLayout()

        export_hint = QLabel("Использует JSON-настройки экспорта и выбранные города")
        export_hint.setWordWrap(True)

        export_buttons_layout = QHBoxLayout()
        self._setup_export_buttons(export_buttons_layout)

        export_actions_layout.addWidget(export_hint)
        export_actions_layout.addLayout(export_buttons_layout)

        export_actions_group.setLayout(export_actions_layout)

        export_actions_group.setMaximumHeight(export_actions_group.sizeHint().height())

        actions_layout.addWidget(city_actions_group)
        actions_layout.addSpacing(12)
        actions_layout.addWidget(export_actions_group)
        actions_layout.addStretch()

        city_main_layout.addLayout(actions_layout)

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

        self.btn_open_file = QPushButton("Открыть файл", self)
        self.btn_open_file.setToolTip("Открыть JSON-файл с городами")
        self.btn_open_file.clicked.connect(self.open_file_dialog)
        layout.addWidget(self.btn_open_file)

        self.btn_save_file_main = QPushButton("Сохранить", self)
        self.btn_save_file_main.setToolTip("Сохранить текущий JSON-файл с городами")
        self.btn_save_file_main.clicked.connect(self.save_file)
        layout.addWidget(self.btn_save_file_main)
        self.btn_save_file_main.setEnabled(False)

        self.btn_del_city = QPushButton("Удалить")
        self.btn_del_city.setToolTip("Удалить выбранные города")
        self.btn_del_city.clicked.connect(self.delete_selected_cities)
        layout.addWidget(self.btn_del_city)

        self.btn_get_sunset_info = QPushButton("Обновить", self)
        self.btn_get_sunset_info.setToolTip("Обновить выбранные данные закатов")
        self.btn_get_sunset_info.clicked.connect(self.initiate_sunset_fetch)
        layout.addWidget(self.btn_get_sunset_info)

        self.btn_del_city.setEnabled(False)
        self.btn_get_sunset_info.setEnabled(False)

    def _setup_export_buttons(self, layout: QHBoxLayout) -> None:
        self.preview_image_button = QPushButton("Предпросмотр", self)
        self.preview_image_button.setToolTip(
            "Предпросмотр перед сохранением изображения"
        )
        self.preview_image_button.clicked.connect(self.preview_selected_city_image)
        layout.addWidget(self.preview_image_button)

        self.btn_export_image = QPushButton("Экспорт", self)
        self.btn_export_image.setToolTip("Экспорт выбранных городов в изображение")
        self.btn_export_image.clicked.connect(self.export_all_selected_city_image)
        layout.addWidget(self.btn_export_image)

        self.image_export_settings_button = QPushButton("Настройки", self)

        image_export_settings_menu = QMenu(self)

        create_settings_action = QAction("Создать настройки", self)
        create_settings_action.triggered.connect(self.create_image_export_settings)
        image_export_settings_menu.addAction(create_settings_action)

        edit_settings_action = QAction("Редактировать настройки", self)
        edit_settings_action.triggered.connect(self.edit_image_export_settings)
        image_export_settings_menu.addAction(edit_settings_action)

        self.image_export_settings_button.setMenu(image_export_settings_menu)
        layout.addWidget(self.image_export_settings_button)

        self.preview_image_button.setEnabled(False)
        self.btn_export_image.setEnabled(False)

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
        date_group = QGroupBox("Параметры расчёта закатов")
        date_group.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed,
        )

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

        date_group_layout.addWidget(QLabel("Дни недели для расчёта:"))
        date_group_layout.addWidget(self.combo_weekday1)
        date_group_layout.addWidget(QLabel("и"))
        date_group_layout.addWidget(self.combo_weekday2)

        date_group.setLayout(date_group_layout)
        date_group.setMaximumHeight(date_group.sizeHint().height())
        self.main_layout.addWidget(date_group)

    def connect_city_model_signals(self, model: CityTableModel) -> None:
        model.dataChanged.connect(self.on_data_changed)
        model.dataChanged.connect(lambda: self.update_action_buttons_state())

        model.selection_changed.connect(self.update_status_bar)
        model.selection_changed.connect(self.update_action_buttons_state)

    def setup_city_model(self, cities: list[City]) -> None:
        self.cities = cities
        self.model = CityTableModel(self.cities)
        self.connect_city_model_signals(self.model)
        self.update_status_bar()
        self.table_view.setModel(self.model)
        self.table_view.show()
        self.initial_prompt_text.hide()
        self.table_view.resizeColumnsToContents()
        self.update_action_buttons_state()

    def show_no_cities_warning(self) -> None:
        show_warning(
            self,
            "Города",
            "Сначала загрузите или создайте города.",
        )

    def on_data_changed(
        self,
        top_left: QModelIndex,
        bottom_right: QModelIndex,
        roles: list[int],
    ) -> None:
        if self.model is None:
            self.show_no_cities_warning()
            return

        if Qt.ItemDataRole.EditRole not in roles:
            return

        self.model.update_status_for_row(top_left.row())
        self.table_view.resizeColumnToContents(STATUS_COLUMN)

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

            update_city_sunset(city, year, weekday1, weekday2)

            self.model.refresh_status_row(row)

        self.table_view.resizeColumnToContents(STATUS_COLUMN)

    def on_city_data_changed(self, row: int):
        """Обработчик изменения данных города через окно редактирования"""
        if self.model is None:
            self.show_no_cities_warning()
            return

        city = self.model.cities[row]
        city.sunset_data.hash_before_edit = city.get_stable_hash()

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

    def initiate_sunset_fetch(self) -> None:
        cities = self.get_selected_cities_or_none()

        if cities is None:
            show_warning(
                self,
                "Обновление данных",
                "Выберите хотя бы один город.",
            )
            return

        model = self.model
        if model is None:
            return

        year = self.year_spinbox.value()
        weekday1 = self.combo_weekday1.currentIndex()
        weekday2 = self.combo_weekday2.currentIndex()

        update_cities_sunset(cities, year, weekday1, weekday2)

        model.clear_status_overrides_for_cities(cities)
        model.refresh_status_column()
        self.table_view.resizeColumnToContents(STATUS_COLUMN)

    def export_all_selected_city_image(self) -> None:
        cities = self.get_selected_cities_or_none()
        if cities is None:
            self.show_no_cities_warning()
            return

        settings_path = self.choose_export_settings_file()
        if settings_path is None:
            return

        output_dir = self.choose_image_export_output_dir()
        if output_dir is None:
            return

        results = export_cities_images(
            cities=cities,
            settings_path=settings_path,
            output_dir=Path(output_dir),
        )

        save_export_report(results, Path(output_dir))
        self.show_image_export_result(results, output_dir)

    def preview_selected_city_image(self) -> None:
        city = self.get_current_city_or_none()

        if city is None:
            show_warning(
                self,
                "Предпросмотр изображения",
                "Выберите город.",
            )
            return

        settings_path = self.choose_export_settings_file()
        if settings_path is None:
            return

        try:
            image = build_city_image_preview(
                city=city,
                settings_path=settings_path,
            )
        except Exception as error:
            show_error(
                self,
                "Ошибка предпросмотра",
                get_user_friendly_error(error),
            )
            return

        self.show_image_preview(image)

    def edit_image_export_settings(self) -> None:
        settings_path = self.choose_export_settings_file()
        if settings_path is None:
            return

        try:
            settings = load_export_settings(settings_path)
        except ImageExportError as error:
            show_error(
                self,
                "Ошибка настроек экспорта",
                get_user_friendly_error(error),
            )
            return
        except Exception as error:
            show_error(
                self,
                "Ошибка настроек экспорта",
                str(error),
            )
            return

        city = self.get_current_city_or_none()

        dialog = ImageExportSettingsDialog(
            settings=settings,
            settings_path=settings_path,
            city=city,
            parent=self,
        )
        dialog.exec()

    def open_file_dialog(self) -> None:
        file_path = choose_file(
            self,
            "Выберите файл",
            "JSON Files (*.json)",
        )

        if not file_path:
            return

        result, error = load_cities_from_file(file_path)

        if error is not None:
            if ask_retry(self, "Ошибка", f"{error}\n\nВыбрать файл снова?"):
                self.open_file_dialog()
            return

        if result is None:
            return

        self.file_path = file_path
        self.update_window_title()
        self.setup_city_model(result)
        self.update_action_buttons_state()
        self.update_status_bar()

    def save_file(self) -> None:
        if self.file_path is None:
            self.save_file_as()
            return

        save_cities_to_file(self.cities, self.file_path)
        self.update_status_bar()

    def save_file_as(self) -> None:
        file_path = choose_save_file(
            self, "Сохранить файл как...", "JSON Files (*.json)"
        )

        if not file_path:
            return

        save_cities_to_file(self.cities, file_path)
        self.file_path = file_path
        self.update_window_title()
        self.update_status_bar()
        self.update_action_buttons_state()

    def add_city_in_table(self) -> None:
        new_city = create_default_city(self.year_spinbox.value())
        if not hasattr(self, "model") or self.model is None:
            self.setup_city_model([new_city])
        else:
            self.model.add_city(new_city)
            if len(self.cities) == 1:
                self.initial_prompt_text.hide()
                self.table_view.show()

        self.table_view.resizeColumnsToContents()
        self.update_action_buttons_state()
        self.update_status_bar()

    def delete_selected_cities(self) -> None:
        if hasattr(self, "model") and self.model is not None:
            self.model.remove_checked_cities()

            self.update_action_buttons_state()
            self.update_status_bar()

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
            return None

        cities = self.model.get_selected_city()
        if not cities:
            return None

        return cities

    def update_action_buttons_state(self) -> None:
        has_selected_cities = False

        if self.model is not None:
            has_selected_cities = bool(self.model.get_selected_city())

        if has_selected_cities:
            self.btn_del_city.setToolTip("Удалить выбранные города")
            self.btn_get_sunset_info.setToolTip("Обновить выбранные данные закатов")
            self.preview_image_button.setToolTip(
                "Предпросмотр перед сохранением изображения"
            )
            self.btn_export_image.setToolTip("Экспорт выбранных городов в изображение")
        else:
            tooltip = "Выберите один или несколько городов в таблице"
            self.btn_del_city.setToolTip(tooltip)
            self.btn_get_sunset_info.setToolTip(tooltip)
            self.preview_image_button.setToolTip(tooltip)
            self.btn_export_image.setToolTip(tooltip)

        for button in (
            self.btn_del_city,
            self.btn_get_sunset_info,
            self.preview_image_button,
            self.btn_export_image,
        ):
            button.setEnabled(has_selected_cities)

        has_cities = bool(self.cities)
        self.btn_save_file_main.setEnabled(has_cities)

    def update_status_bar(self) -> None:
        file_name = "Файл не открыт"
        if self.file_path is not None:
            file_name = f"Файл: {Path(self.file_path).name}"

        total_cities = len(self.cities)
        selected_cities = 0

        if self.model is not None:
            selected = self.model.get_selected_city()
            selected_cities = len(selected) if selected else 0

        self.status_bar.showMessage(
            f"{file_name} | Городов: {total_cities} | Выбрано: {selected_cities}"
        )

    def update_window_title(self) -> None:
        if self.file_path is None:
            self.setWindowTitle("Sun set")
        else:
            self.setWindowTitle(f"Sun set — {Path(self.file_path).name}")

    def choose_export_settings_file(self) -> Path | None:
        settings_file = choose_file(
            self,
            "Выберите JSON-файл настроек экспорта",
            "JSON Files (*.json)",
            self.last_image_export_settings_path,
        )

        if not settings_file:
            return None

        self.last_image_export_settings_path = settings_file
        return Path(settings_file)

    def choose_image_export_output_dir(self) -> Path | None:
        output_dir = choose_directory(
            self,
            "Выберите папку, куда сохранить изображения",
            self.last_image_export_output_dir,
        )

        if not output_dir:
            return None

        self.last_image_export_output_dir = output_dir
        return Path(output_dir)

    def show_image_export_result(
        self,
        results: list[ExportResult],
        output_dir: Path,
    ) -> None:
        message = build_export_summary_message(results)

        if ask_open_folder_after_export(self, message):
            open_directory(output_dir)

    def show_image_preview(self, image: Image.Image) -> None:
        dialog = ImagePreviewDialog(
            image=image,
            parent=self,
        )
        dialog.exec()
