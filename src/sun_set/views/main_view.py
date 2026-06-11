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
from sun_set.models.project_data import ProjectData
from sun_set.models.table_model import (
    STATUS_COLUMN,
    CheckBoxHeader,
    CityTableModel,
    StatusActionDelegate,
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
from sun_set.services.project_file_service import load_project, save_project
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

        self.main_layout.setContentsMargins(12, 8, 12, 8)
        self.main_layout.setSpacing(8)

        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)
        self.update_status_bar()

        self._setup_menu()
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
        city_main_layout.setSpacing(8)

        date_group = self._create_date_group()
        city_actions_group = self._create_city_actions_group()
        export_actions_group = self._create_export_actions_group()

        city_main_layout.addWidget(date_group)
        city_main_layout.addWidget(city_actions_group)
        city_main_layout.addWidget(export_actions_group)

        self.initial_prompt_text = QLabel(
            "Файл с городами не открыт\n\n"
            "Откройте файл с городами или нажмите «Добавить»"
        )
        self.initial_prompt_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.initial_prompt_text.setWordWrap(True)
        city_main_layout.addWidget(self.initial_prompt_text)

        self._setup_table()
        city_main_layout.addWidget(self.table_view)

        city_main_layout.setStretch(0, 0)  # actions
        city_main_layout.setStretch(1, 0)  # empty text
        city_main_layout.setStretch(2, 1)  # table

        city_group.setLayout(city_main_layout)
        self.main_layout.addWidget(city_group)

    def _create_city_actions_group(self) -> QGroupBox:
        city_actions_group = QGroupBox("Города")
        city_actions_layout = QHBoxLayout()

        self._setup_city_buttons(city_actions_layout)

        city_actions_group.setLayout(city_actions_layout)
        city_actions_group.setMaximumHeight(city_actions_group.sizeHint().height())

        return city_actions_group

    def _create_export_actions_group(self) -> QGroupBox:
        export_actions_group = QGroupBox("Изображения")
        export_actions_layout = QVBoxLayout()

        self.export_paths_label = QLabel("Настройки: не выбраны | Папка: не выбрана")

        export_buttons_layout = QHBoxLayout()
        self._setup_export_buttons(export_buttons_layout)

        export_actions_layout.addWidget(self.export_paths_label)
        export_actions_layout.addLayout(export_buttons_layout)

        export_actions_group.setLayout(export_actions_layout)
        export_actions_group.setMaximumHeight(export_actions_group.sizeHint().height())
        export_actions_group.setMaximumWidth(760)

        return export_actions_group

    def _setup_city_buttons(self, layout: QHBoxLayout) -> None:
        self.btn_add_city = QPushButton("Добавить")
        self.btn_add_city.setToolTip("Добавить город в таблицу")
        self.btn_add_city.clicked.connect(self.add_city_in_table)
        self.setup_action_button(self.btn_add_city)
        layout.addWidget(self.btn_add_city)

        self.btn_open_file = QPushButton("Открыть файл", self)
        self.btn_open_file.setToolTip("Открыть JSON-файл с городами")
        self.btn_open_file.clicked.connect(self.open_file_dialog)
        self.setup_action_button(self.btn_open_file)
        layout.addWidget(self.btn_open_file)

        self.btn_save_file_main = QPushButton("Сохранить", self)
        self.btn_save_file_main.setToolTip("Сохранить текущий JSON-файл с городами")
        self.btn_save_file_main.clicked.connect(self.save_file)
        self.setup_action_button(self.btn_save_file_main)
        layout.addWidget(self.btn_save_file_main)

        self.btn_del_city = QPushButton("Удалить")
        self.btn_del_city.setToolTip("Удалить выбранные города")
        self.btn_del_city.clicked.connect(self.delete_selected_cities)
        self.setup_action_button(self.btn_del_city)
        layout.addWidget(self.btn_del_city)

        self.btn_get_sunset_info = QPushButton("Обновить", self)
        self.btn_get_sunset_info.setToolTip("Обновить выбранные данные закатов")
        self.btn_get_sunset_info.clicked.connect(self.initiate_sunset_fetch)
        self.setup_action_button(self.btn_get_sunset_info)
        layout.addWidget(self.btn_get_sunset_info)

        self.btn_save_file_main.setEnabled(False)
        self.btn_del_city.setEnabled(False)
        self.btn_get_sunset_info.setEnabled(False)

    def _setup_export_buttons(self, layout: QHBoxLayout) -> None:
        self.btn_change_export_settings = QPushButton("Выбрать настройки", self)
        self.btn_change_export_dir = QPushButton("Выбрать папку", self)

        self.btn_change_export_settings.clicked.connect(
            self.select_export_settings_file
        )
        self.btn_change_export_dir.clicked.connect(self.select_export_output_dir)
        self.setup_action_button(self.btn_change_export_settings)
        self.setup_action_button(self.btn_change_export_dir)

        layout.addWidget(self.btn_change_export_settings)
        layout.addWidget(self.btn_change_export_dir)

        self.preview_image_button = QPushButton("Предпросмотр", self)
        self.preview_image_button.setToolTip(
            "Предпросмотр перед сохранением изображения"
        )
        self.preview_image_button.clicked.connect(self.preview_selected_city_image)
        self.setup_action_button(self.preview_image_button)
        layout.addWidget(self.preview_image_button)

        self.btn_export_image = QPushButton("Экспорт", self)
        self.btn_export_image.setToolTip("Экспорт выбранных городов в изображение")
        self.btn_export_image.clicked.connect(self.export_all_selected_city_image)
        self.setup_action_button(self.btn_export_image)
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
        self.setup_action_button(self.image_export_settings_button)
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

    def _create_date_group(self) -> QGroupBox:
        date_group = QGroupBox("Дни расчёта")
        date_group.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed,
        )

        date_group_layout = QHBoxLayout()
        date_group_layout.setContentsMargins(12, 8, 12, 8)
        date_group_layout.setSpacing(8)

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

        self.year_spinbox.valueChanged.connect(self.update_window_title)
        self.combo_weekday1.currentIndexChanged.connect(self.update_window_title)
        self.combo_weekday2.currentIndexChanged.connect(self.update_window_title)

        date_group.setLayout(date_group_layout)
        date_group.setMaximumHeight(date_group.sizeHint().height())
        date_group.setMaximumWidth(date_group.sizeHint().width())
        date_group.setMaximumWidth(520)
        return date_group

    def connect_city_model_signals(self, model: CityTableModel) -> None:
        model.dataChanged.connect(self.on_data_changed)
        model.dataChanged.connect(lambda: self.update_action_buttons_state())

        model.selection_changed.connect(self.update_status_bar)
        model.selection_changed.connect(self.update_action_buttons_state)

    def show_city_model(self, model: CityTableModel) -> None:
        self.table_view.setModel(model)
        self.table_view.show()
        self.initial_prompt_text.hide()
        self.table_view.resizeColumnsToContents()

    def load_cities_into_table(self, cities: list[City]) -> None:
        self.cities = cities
        self.model = CityTableModel(self.cities)

        self.connect_city_model_signals(self.model)
        self.show_city_model(self.model)

        self.update_status_bar()
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

    def update_city_row_display(self, row: int) -> None:
        if self.model is None:
            self.show_no_cities_warning()
            return

        self.model.refresh_status_row(row)

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

        settings_path = self.get_export_settings_path()
        if settings_path is None:
            return

        output_dir = self.get_export_output_dir()
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

        settings_path = self.get_export_settings_path()
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
        settings_path = self.get_export_settings_path()
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

        project, error = load_project(file_path)

        if error is not None:
            if ask_retry(self, "Ошибка", f"{error}\n\nВыбрать файл снова?"):
                self.open_file_dialog()
            return

        if project is None:
            return

        self.file_path = file_path
        self.update_window_title()
        self.apply_project_data(project)
        self.update_window_title()
        self.update_action_buttons_state()
        self.update_status_bar()

    def save_file(self) -> None:
        if self.file_path is None:
            self.save_file_as()
            return

        project = self.build_current_project_data()
        save_project(project, self.file_path)
        self.update_status_bar()

    def save_file_as(self) -> None:
        file_path = choose_save_file(
            self, "Сохранить файл как...", "JSON Files (*.json)"
        )

        if not file_path:
            return

        project = self.build_current_project_data()
        save_project(project, file_path)
        self.file_path = file_path
        self.update_window_title()
        self.update_status_bar()
        self.update_action_buttons_state()

    def add_city_in_table(self) -> None:
        new_city = create_default_city(self.year_spinbox.value())

        if self.model is None:
            self.load_cities_into_table([new_city])
        else:
            self.model.add_city(new_city)
            self.cities = self.model.cities
            self.table_view.resizeColumnsToContents()

        self.update_action_buttons_state()
        self.update_status_bar()

    def delete_selected_cities(self) -> None:
        if self.model is None:
            return

        self.model.remove_checked_cities()
        self.table_view.resizeColumnsToContents()

        self.cities = self.model.cities

        if not self.cities:
            self.show_empty_city_state()

        self.update_action_buttons_state()
        self.update_status_bar()

    def show_empty_city_state(self) -> None:
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

        cities = self.model.get_selected_cities()
        if not cities:
            return None

        return cities[0]

    def get_selected_cities_or_none(self) -> list[City] | None:
        if self.model is None:
            return None

        cities = self.model.get_selected_cities()
        if not cities:
            return None

        return cities

    def update_action_buttons_state(self) -> None:
        has_selected_cities = False

        if self.model is not None:
            has_selected_cities = bool(self.model.get_selected_cities())

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
            selected = self.model.get_selected_cities()
            selected_cities = len(selected) if selected else 0

        self.status_bar.showMessage(
            f"{file_name} | Городов: {total_cities} | Выбрано: {selected_cities}"
        )

    def update_window_title(self) -> None:
        if self.file_path is None:
            self.setWindowTitle("Sun Set")
            return

        self.setWindowTitle(f"Sun Set — {Path(self.file_path).name}")

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
        self.update_export_paths_label()

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
        self.update_export_paths_label()

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

    def build_current_project_data(self) -> ProjectData:
        return ProjectData(
            year=self.year_spinbox.value(),
            weekday1=self.combo_weekday1.currentIndex(),
            weekday2=self.combo_weekday2.currentIndex(),
            cities=self.cities,
            export_settings_path=self.last_image_export_settings_path or None,
            export_output_dir=self.last_image_export_output_dir or None,
        )

    def apply_project_data(self, project: ProjectData) -> None:
        self.year_spinbox.setValue(project.year)
        self.combo_weekday1.setCurrentIndex(project.weekday1)
        self.combo_weekday2.setCurrentIndex(project.weekday2)

        self.last_image_export_settings_path = project.export_settings_path or ""
        self.last_image_export_output_dir = project.export_output_dir or ""

        self.update_export_paths_label()

        self.load_cities_into_table(project.cities)

    def update_export_paths_label(self) -> None:
        settings_text = "не выбраны"
        output_dir_text = "не выбрана"

        tooltip_parts = []

        if self.last_image_export_settings_path:
            settings_path = Path(self.last_image_export_settings_path)
            settings_text = settings_path.name
            tooltip_parts.append(f"Файл настроек: {settings_path}")

        if self.last_image_export_output_dir:
            output_dir = Path(self.last_image_export_output_dir)
            output_dir_text = output_dir.name
            tooltip_parts.append(f"Папка экспорта: {output_dir}")

        self.export_paths_label.setText(
            f"Настройки: {settings_text} | Папка: {output_dir_text}"
        )
        self.export_paths_label.setToolTip("\n".join(tooltip_parts))

    def get_export_settings_path(self) -> Path | None:
        if self.last_image_export_settings_path:
            settings_path = Path(self.last_image_export_settings_path)

            if settings_path.exists():
                return settings_path

            show_warning(
                self,
                "Настройки экспорта",
                "Сохранённый файл настроек экспорта не найден. Выберите файл заново.",
            )
            self.last_image_export_settings_path = ""
            self.update_export_paths_label()

        return self.choose_export_settings_file()

    def get_export_output_dir(self) -> Path | None:
        if self.last_image_export_output_dir:
            output_dir = Path(self.last_image_export_output_dir)

            if output_dir.exists():
                return output_dir

            show_warning(
                self,
                "Экспорт изображений",
                "Сохранённая папка экспорта не найдена. Выберите папку заново.",
            )
            self.last_image_export_output_dir = ""
            self.update_export_paths_label()

        return self.choose_image_export_output_dir()

    def select_export_settings_file(self) -> None:
        self.choose_export_settings_file()

    def select_export_output_dir(self) -> None:
        self.choose_image_export_output_dir()

    def setup_action_button(self, button: QPushButton) -> None:
        button.setMinimumWidth(120)
        button.setMaximumWidth(180)
