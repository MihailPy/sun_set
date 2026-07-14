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

from sun_set.constants.messages import (
    EXPORT_IMAGES_TITLE,
    EXPORT_SETTINGS_TITLE,
    IMAGE_EXPORT_ERROR_TITLE,
    IMAGE_PREVIEW_ERROR_TITLE,
    IMAGE_PREVIEW_TITLE,
    MISSING_EXPORT_OUTPUT_DIR_MESSAGE,
    MISSING_EXPORT_SETTINGS_FILE_MESSAGE,
)
from sun_set.constants.project_defaults import (
    DEFAULT_WEEKDAY_1,
    DEFAULT_WEEKDAY_2,
    get_default_project_year,
)
from sun_set.image_export.settings import ExportImageSettings
from sun_set.models.city import City
from sun_set.models.project_data import ProjectData
from sun_set.models.table_model import (
    STATUS_COLUMN,
    SUNSET_DATA_COLUMN,
    CheckBoxHeader,
    CityTableModel,
    can_open_city_sunset_data,
)
from sun_set.services.dialog_service import (
    ask_retry,
    choose_directory,
    choose_file,
    choose_save_file,
    show_error,
    show_warning,
)
from sun_set.services.image_export_workflow import (
    ImageExportSettingsLoadSuccess,
    ImageExportSuccessResult,
    ImagePreviewSuccessResult,
    build_image_export_request,
    build_image_preview_request,
    create_default_image_export_settings,
    execute_image_export,
    execute_image_export_settings_load,
    execute_image_preview,
    show_image_export_result_dialog,
)
from sun_set.services.project_state_service import (
    ExportPaths,
    ExportPathState,
    build_export_action_tooltip,
    build_export_paths_text,
    build_export_paths_tooltip,
    build_project_data,
    can_export_images,
    can_preview_image,
    export_output_dir_exists,
    export_settings_path_exists,
    get_export_paths_from_project,
    get_project_settings,
)
from sun_set.services.project_window_state import ProjectWindowState
from sun_set.services.project_workflow import (
    ProjectLoadSuccess,
    ProjectSaveSuccess,
    execute_project_load,
    execute_project_save,
)
from sun_set.services.sunset_workflow import (
    SunsetSettings,
    build_sunset_update_request,
    create_city_for_year,
    execute_sunset_update,
)
from sun_set.views.about_dialog import AboutDialog
from sun_set.views.delegates.custom_delegate import CityDelegate
from sun_set.views.image_export_settings_dialog import ImageExportSettingsDialog
from sun_set.views.image_preview_dialog import ImagePreviewDialog
from sun_set.views.sunset_table_view import YearEditorWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Sun set")
        self.resize(800, 400)

        self.project_window_state = ProjectWindowState()
        self.export_path_state = ExportPathState.empty()

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

        help_menu = menu.addMenu("&Справка")
        if help_menu:
            about_action = QAction("О программе", self)
            about_action.triggered.connect(self.open_about_dialog)
            help_menu.addAction(about_action)

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
            "Откройте JSON-файл проекта\n"
            "или нажмите «Добавить», чтобы создать новый список городов"
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

        self.selected_cities_label = QLabel("Выбрано: 0")

        self._setup_city_buttons(city_actions_layout)

        city_actions_layout.addStretch()
        city_actions_layout.addWidget(self.selected_cities_label)

        city_actions_group.setLayout(city_actions_layout)
        city_actions_group.setMaximumHeight(city_actions_group.sizeHint().height())
        city_actions_group.setMaximumWidth(city_actions_group.sizeHint().width())

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
        export_actions_group.setMaximumWidth(export_actions_group.sizeHint().width())

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

        self.setup_table_header()
        self.setup_table_delegates()
        self.connect_table_signals()

        self.table_view.hide()

    def _create_date_group(self) -> QGroupBox:
        date_group = QGroupBox("Дни расчёта")
        date_group.setSizePolicy(
            QSizePolicy.Policy.Maximum,
            QSizePolicy.Policy.Fixed,
        )

        date_group_layout = QHBoxLayout()
        date_group_layout.setContentsMargins(12, 8, 12, 8)
        date_group_layout.setSpacing(8)

        default_year = get_default_project_year()

        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(default_year - 51, default_year + 49)
        self.year_spinbox.setValue(default_year)

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

        self.combo_weekday1.setCurrentIndex(DEFAULT_WEEKDAY_1)
        self.combo_weekday2.setCurrentIndex(DEFAULT_WEEKDAY_2)

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
        return date_group

    def connect_city_model_signals(self, model: CityTableModel) -> None:
        model.dataChanged.connect(self.on_data_changed)
        model.dataChanged.connect(lambda: self.update_action_buttons_state())

        model.selection_changed.connect(self.update_status_bar)
        model.selection_changed.connect(self.update_action_buttons_state)

    def show_city_model(self, model: CityTableModel) -> None:
        self.table_view.setModel(model)
        self.show_table_view()
        self.resize_table_columns()

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

        settings = self.get_current_sunset_settings()

        request = build_sunset_update_request(
            cities=cities,
            settings=settings,
        )

        execute_sunset_update(request)

        self.refresh_sunset_update_result(model, cities)

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

        request = build_image_export_request(
            cities=cities,
            settings_path=settings_path,
            output_dir=output_dir,
        )

        execution_result = execute_image_export(request)

        if not isinstance(execution_result, ImageExportSuccessResult):
            show_error(
                self,
                IMAGE_EXPORT_ERROR_TITLE,
                execution_result.error_message,
            )
            return

        show_image_export_result_dialog(
            self,
            execution_result.results,
            output_dir,
        )

    def preview_selected_city_image(self) -> None:
        city = self.get_first_selected_city_or_none()
        if city is None:
            show_warning(
                self,
                IMAGE_PREVIEW_TITLE,
                "Выберите город.",
            )
            return

        settings_path = self.get_export_settings_path()
        if settings_path is None:
            return

        request = build_image_preview_request(
            city=city,
            settings_path=settings_path,
        )

        execution_result = execute_image_preview(request)

        if not isinstance(execution_result, ImagePreviewSuccessResult):
            show_error(
                self,
                IMAGE_PREVIEW_ERROR_TITLE,
                execution_result.error_message,
            )
            return

        self.open_image_preview_dialog(execution_result.image)

    def edit_image_export_settings(self) -> None:
        settings_path = self.get_export_settings_path()
        if settings_path is None:
            return

        load_result = execute_image_export_settings_load(settings_path)

        if not isinstance(load_result, ImageExportSettingsLoadSuccess):
            show_error(
                self,
                "Ошибка настроек экспорта",
                load_result.message,
            )
            return

        settings = load_result.settings

        self.open_image_export_settings_dialog(
            settings=settings,
            settings_path=settings_path,
        )

    def open_file_dialog(self) -> None:
        file_path = choose_file(
            self,
            "Выберите файл",
            "JSON Files (*.json)",
        )

        if not file_path:
            return

        project = self.load_project_from_path(file_path)
        if project is None:
            return

        self.open_project(file_path, project)

    def save_file(self) -> None:
        if self.project_window_state.file_path is None:
            self.save_file_as()
            return

        self.save_project_to_path(self.project_window_state.file_path)

    def save_file_as(self) -> None:
        file_path = choose_save_file(
            self, "Сохранить файл как...", "JSON Files (*.json)"
        )

        if not file_path:
            return

        self.save_project_to_path(file_path)

    def add_city_in_table(self) -> None:
        new_city = create_city_for_year(self.year_spinbox.value())

        if self.model is None:
            self.load_cities_into_table([new_city])
        else:
            self.model.add_city(new_city)
            self.cities = self.model.cities
            self.resize_table_columns()

        self.update_action_buttons_state()
        self.update_status_bar()

    def delete_selected_cities(self) -> None:
        if self.model is None:
            return

        self.model.remove_selected_cities()
        self.resize_table_columns()

        self.cities = self.model.cities

        if not self.cities:
            self.show_empty_city_state()

        self.update_action_buttons_state()
        self.update_status_bar()

    def show_empty_city_state(self) -> None:
        self.table_view.hide()
        self.setup_table_header()
        self.initial_prompt_text.show()

    def create_image_export_settings(self) -> None:
        settings = create_default_image_export_settings()
        self.open_image_export_settings_dialog(
            settings=settings,
            settings_path=None,
        )

    def get_first_selected_city_or_none(self) -> City | None:
        cities = self.get_selected_cities()
        return cities[0] if cities else None

    def get_selected_cities_or_none(self) -> list[City] | None:
        cities = self.get_selected_cities()
        return cities or None

    def update_action_buttons_state(self) -> None:
        has_selected_cities = self.has_selected_cities()
        export_paths = self.get_current_export_paths()

        self.update_city_action_buttons_state(has_selected_cities)
        self.update_export_action_buttons_state(
            has_selected_cities,
            export_paths,
        )

    def update_status_bar(self) -> None:
        self.update_selected_cities_label()
        self.status_bar.showMessage(self.build_status_bar_text())

    def update_window_title(self) -> None:
        file_name = self.project_window_state.get_file_name()

        if file_name is None:
            self.setWindowTitle("Sun Set")
            return

        self.setWindowTitle(f"Sun Set — {file_name}")

    def choose_export_settings_file(self) -> Path | None:
        settings_file = choose_file(
            self,
            "Выберите JSON-файл настроек экспорта",
            "JSON Files (*.json)",
            self.get_current_export_paths().settings_path,
        )

        if not settings_file:
            return None

        self.export_path_state.set_settings_path(str(settings_file))
        self.update_export_paths_label()

        return Path(settings_file)

    def choose_image_export_output_dir(self) -> Path | None:
        output_dir = choose_directory(
            self,
            "Выберите папку, куда сохранить изображения",
            self.get_current_export_paths().output_dir,
        )

        if not output_dir:
            return None

        self.export_path_state.set_output_dir(str(output_dir))
        self.update_export_paths_label()

        return Path(output_dir)

    def open_image_preview_dialog(self, image: Image.Image) -> None:
        dialog = ImagePreviewDialog(
            image=image,
            parent=self,
        )
        dialog.exec()

    def build_current_project_data(self) -> ProjectData:
        export_paths = self.get_current_export_paths()

        return build_project_data(
            year=self.year_spinbox.value(),
            weekday1=self.combo_weekday1.currentIndex(),
            weekday2=self.combo_weekday2.currentIndex(),
            cities=self.cities,
            export_settings_path=export_paths.settings_path,
            export_output_dir=export_paths.output_dir,
        )

    def apply_project_data(self, project: ProjectData) -> None:
        self.apply_project_settings(project)
        self.apply_export_paths(project)
        self.load_cities_into_table(project.cities)

    def update_export_paths_label(self) -> None:
        export_paths = self.get_current_export_paths()

        self.export_paths_label.setText(build_export_paths_text(export_paths))
        self.export_paths_label.setToolTip(build_export_paths_tooltip(export_paths))
        self.update_action_buttons_state()

    def get_export_settings_path(self) -> Path | None:
        export_paths = self.get_current_export_paths()

        if export_paths.settings_path:
            if export_settings_path_exists(export_paths):
                return Path(export_paths.settings_path)

            show_warning(
                self,
                EXPORT_SETTINGS_TITLE,
                MISSING_EXPORT_SETTINGS_FILE_MESSAGE,
            )
            self.export_path_state.clear_settings_path()
            self.update_export_paths_label()

        return self.choose_export_settings_file()

    def get_export_output_dir(self) -> Path | None:
        export_paths = self.get_current_export_paths()

        if export_paths.output_dir:
            if export_output_dir_exists(export_paths):
                return Path(export_paths.output_dir)

            show_warning(
                self,
                EXPORT_IMAGES_TITLE,
                MISSING_EXPORT_OUTPUT_DIR_MESSAGE,
            )
            self.export_path_state.clear_output_dir()
            self.update_export_paths_label()

        return self.choose_image_export_output_dir()

    def select_export_settings_file(self) -> None:
        self.choose_export_settings_file()

    def select_export_output_dir(self) -> None:
        self.choose_image_export_output_dir()

    def setup_action_button(self, button: QPushButton) -> None:
        button.setMinimumWidth(120)
        button.setMaximumWidth(180)

    def get_selected_cities_count(self) -> int:
        return len(self.get_selected_cities())

    def has_selected_cities(self) -> bool:
        return self.get_selected_cities_count() > 0

    def has_cities(self) -> bool:
        return bool(self.cities)

    def get_status_file_text(self) -> str:
        return self.project_window_state.get_status_file_text()

    def build_status_bar_text(self) -> str:
        return (
            f"{self.get_status_file_text()} | "
            f"Городов: {len(self.cities)} | "
            f"Выбрано: {self.get_selected_cities_count()}"
        )

    def update_selected_cities_label(self) -> None:
        if not hasattr(self, "selected_cities_label"):
            return

        self.selected_cities_label.setText(
            f"Выбрано: {self.get_selected_cities_count()}"
        )

    def apply_project_settings(self, project: ProjectData) -> None:
        settings = get_project_settings(project)

        self.year_spinbox.setValue(settings.year)
        self.combo_weekday1.setCurrentIndex(settings.weekday1)
        self.combo_weekday2.setCurrentIndex(settings.weekday2)

    def apply_export_paths(self, project: ProjectData) -> None:
        export_paths = get_export_paths_from_project(project)

        self.export_path_state.set_paths(export_paths)
        self.update_export_paths_label()

    def get_current_export_paths(self) -> ExportPaths:
        return self.export_path_state.paths

    def load_project_from_path(self, file_path: str) -> ProjectData | None:
        result = execute_project_load(file_path)

        if not isinstance(result, ProjectLoadSuccess):
            if ask_retry(self, "Ошибка", f"{result.message}\n\nВыбрать файл снова?"):
                self.open_file_dialog()
            return None

        return result.project

    def open_project(self, file_path: str, project: ProjectData) -> None:
        self.project_window_state.file_path = file_path
        self.apply_project_data(project)
        self.update_window_title()
        self.update_action_buttons_state()
        self.update_status_bar()

    def save_project_to_path(self, file_path: str) -> None:
        project = self.build_current_project_data()
        result = execute_project_save(project, file_path)

        if not isinstance(result, ProjectSaveSuccess):
            show_error(
                self,
                "Ошибка сохранения",
                result.message,
            )
            return

        self.project_window_state.file_path = result.file_path
        self.update_window_title()
        self.update_status_bar()
        self.update_action_buttons_state()

    def refresh_sunset_update_result(
        self,
        model: CityTableModel,
        cities: list[City],
    ) -> None:
        model.refresh_status_column()
        self.table_view.resizeColumnToContents(STATUS_COLUMN)

    def get_current_sunset_settings(self) -> SunsetSettings:
        return SunsetSettings(
            year=self.year_spinbox.value(),
            weekday1=self.combo_weekday1.currentIndex(),
            weekday2=self.combo_weekday2.currentIndex(),
        )

    def open_city_sunset_data(self, row: int) -> None:
        if self.model is None:
            self.show_no_cities_warning()
            return

        city = self.model.cities[row]
        self.open_year_editor_window(city, row)

    def handle_table_click(self, index: QModelIndex) -> None:
        if index.column() != SUNSET_DATA_COLUMN:
            return

        if self.model is None:
            return

        city = self.model.cities[index.row()]
        if not can_open_city_sunset_data(city):
            return

        self.open_city_sunset_data(index.row())

    def resize_table_columns(self) -> None:
        self.table_view.resizeColumnsToContents()
        self.table_view.setColumnWidth(STATUS_COLUMN, 170)
        self.table_view.setColumnWidth(SUNSET_DATA_COLUMN, 120)

    def open_image_export_settings_dialog(
        self,
        settings: ExportImageSettings,
        settings_path: Path | None,
    ) -> None:
        city = self.get_first_selected_city_or_none()

        dialog = ImageExportSettingsDialog(
            settings=settings,
            settings_path=settings_path,
            city=city,
            parent=self,
        )
        dialog.exec()

    def open_year_editor_window(self, city: City, row: int) -> None:
        self.extra_window = YearEditorWindow(city)
        self.extra_window.dataChanged.connect(lambda: self.on_city_data_changed(row))
        self.extra_window.show()

    def get_selected_cities(self) -> list[City]:
        if self.model is None:
            return []

        return self.model.get_selected_cities() or []

    def get_city_actions_tooltip(self, has_selected_cities: bool) -> str:
        if has_selected_cities:
            return ""

        return "Выберите один или несколько городов в таблице"

    def update_city_action_buttons_state(self, has_selected_cities: bool) -> None:
        self.btn_del_city.setEnabled(has_selected_cities)
        self.btn_get_sunset_info.setEnabled(has_selected_cities)
        self.btn_save_file_main.setEnabled(self.has_cities())

        if has_selected_cities:
            self.btn_del_city.setToolTip("Удалить выбранные города")
            self.btn_get_sunset_info.setToolTip("Обновить выбранные данные закатов")
            return

        city_tooltip = self.get_city_actions_tooltip(has_selected_cities)
        self.btn_del_city.setToolTip(city_tooltip)
        self.btn_get_sunset_info.setToolTip(city_tooltip)

    def update_export_action_buttons_state(
        self,
        has_selected_cities: bool,
        export_paths: ExportPaths,
    ) -> None:
        self.preview_image_button.setEnabled(
            can_preview_image(has_selected_cities, export_paths)
        )
        self.btn_export_image.setEnabled(
            can_export_images(has_selected_cities, export_paths)
        )

        export_tooltip = build_export_action_tooltip(
            has_selected_cities,
            export_paths,
        )

        self.preview_image_button.setToolTip(
            "Предпросмотр перед сохранением изображения"
            if self.preview_image_button.isEnabled()
            else export_tooltip
        )
        self.btn_export_image.setToolTip(
            "Экспорт выбранных городов в изображение"
            if self.btn_export_image.isEnabled()
            else export_tooltip
        )

    def setup_table_header(self) -> None:
        header = CheckBoxHeader(Qt.Orientation.Horizontal, self.table_view)
        self.table_view.setHorizontalHeader(header)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(
            STATUS_COLUMN, QHeaderView.ResizeMode.ResizeToContents
        )
        header.setSectionResizeMode(
            SUNSET_DATA_COLUMN,
            QHeaderView.ResizeMode.ResizeToContents,
        )

    def setup_table_delegates(self) -> None:
        self.table_view.setItemDelegate(CityDelegate(self.table_view))

    def connect_table_signals(self) -> None:
        self.table_view.clicked.connect(self.handle_table_click)

    def show_table_view(self) -> None:
        self.table_view.show()
        self.initial_prompt_text.hide()

    def open_about_dialog(self) -> None:
        dialog = AboutDialog(self)
        dialog.exec()
