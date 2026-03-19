import typing

from PyQt6 import QtGui
from PyQt6.QtCore import (
    QAbstractTableModel,
    QEvent,
    QModelIndex,
    QRect,
    QSize,
    Qt,
    pyqtSignal,
)
from PyQt6.QtGui import QMouseEvent  # Needed for type checking
from PyQt6.QtWidgets import (
    QApplication,
    QHeaderView,
    QStyle,
    QStyledItemDelegate,
    QStyleOptionButton,
)

from sun_set.core.astronmy import get_city_sunset
from sun_set.models.city import City
from sun_set.models.sunset import Source


class StatusActionDelegate(QStyledItemDelegate):
    buttonClicked = pyqtSignal(int, str)  # row, action_type ('view' или 'update')

    # Константы
    BTN_WIDTH = 40  # Уменьшаем ширину для иконок
    MARGIN = 5
    BUTTON_SPACING = 5  # Расстояние между кнопками

    # Роли данных для хранения состояний кнопок
    ViewEnabledRole = Qt.ItemDataRole.UserRole + 1
    UpdateEnabledRole = Qt.ItemDataRole.UserRole + 2

    def sizeHint(self, option, index) -> QSize:
        status_text = f"{index.data() or '✅ Загружено'}"

        # Ширина для двух кнопок + отступы
        buttons_width = self.BTN_WIDTH * 2 + self.BUTTON_SPACING

        text_width = option.fontMetrics.horizontalAdvance(status_text)
        total_width = text_width + buttons_width + (self.MARGIN * 6)

        return QSize(total_width, 40)

    def paint(self, painter, option, index):
        if painter is None:
            return
        self.initStyleOption(option, index)
        painter.save()

        v_margin = 1

        # Прямоугольники для двух кнопок
        view_btn_rect = QRect(
            option.rect.right() - self.BTN_WIDTH * 2 - self.BUTTON_SPACING,
            option.rect.top() + v_margin,
            self.BTN_WIDTH,
            option.rect.height() - 2 * v_margin,
        )

        update_btn_rect = QRect(
            option.rect.right() - self.BTN_WIDTH - self.MARGIN,
            option.rect.top() + v_margin,
            self.BTN_WIDTH,
            option.rect.height() - 2 * v_margin,
        )

        # Текст статуса
        text_rect = QRect(
            option.rect.left() + self.MARGIN,
            option.rect.top(),
            option.rect.width()
            - (self.BTN_WIDTH * 2)
            - self.BUTTON_SPACING
            - (self.MARGIN * 4),
            option.rect.height(),
        )

        status_text = f"{index.data() or '✅ Загружено'}"
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            status_text,
        )

        # Получаем состояния кнопок
        view_enabled = index.data(self.ViewEnabledRole)
        update_enabled = index.data(self.UpdateEnabledRole)

        # Рисуем кнопку "Просмотреть" 👁️
        view_btn_option = QStyleOptionButton()
        view_btn_option.rect = view_btn_rect
        view_btn_option.text = "👁️"  # Эмодзи глаза
        view_btn_option.state = (
            QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
        )

        if view_enabled is False:
            view_btn_option.state &= ~QStyle.StateFlag.State_Enabled

        style = option.widget.style() if option.widget else QApplication.style()
        if style:
            style.drawControl(
                QStyle.ControlElement.CE_PushButton, view_btn_option, painter
            )

        # Рисуем кнопку "Обновить" 🔄
        update_btn_option = QStyleOptionButton()
        update_btn_option.rect = update_btn_rect
        update_btn_option.text = "🔄"  # Эмодзи обновления
        update_btn_option.state = (
            QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
        )

        if update_enabled is False:
            update_btn_option.state &= ~QStyle.StateFlag.State_Enabled

        if style:
            style.drawControl(
                QStyle.ControlElement.CE_PushButton, update_btn_option, painter
            )

        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:
        if event is None:
            return False

        if event.type() == QEvent.Type.MouseButtonRelease:
            if isinstance(event, QMouseEvent):
                pos = event.position().toPoint()

                # Проверяем клик по кнопке "Просмотреть"
                view_btn_rect = QRect(
                    option.rect.right() - self.BTN_WIDTH * 2 - self.BUTTON_SPACING,
                    option.rect.top() + self.MARGIN,
                    self.BTN_WIDTH,
                    option.rect.height() - 2 * self.MARGIN,
                )

                # Проверяем клик по кнопке "Обновить"
                update_btn_rect = QRect(
                    option.rect.right() - self.BTN_WIDTH - self.MARGIN,
                    option.rect.top() + self.MARGIN,
                    self.BTN_WIDTH,
                    option.rect.height() - 2 * self.MARGIN,
                )

                # Получаем состояния кнопок
                view_enabled = index.data(self.ViewEnabledRole)
                update_enabled = index.data(self.UpdateEnabledRole)

                if view_btn_rect.contains(pos):
                    if view_enabled is not False:  # Если кнопка включена
                        self.buttonClicked.emit(index.row(), "view")
                        return True

                if update_btn_rect.contains(pos):
                    if update_enabled is not False:  # Если кнопка включена
                        self.buttonClicked.emit(index.row(), "update")
                        return True

        return super().editorEvent(event, model, option, index)


class CheckBoxHeader(QHeaderView):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent)
        self.is_checked = False

    def paintSection(self, painter, rect, logicalIndex):
        # 1. Проверяем, что painter существует
        if painter is None:
            return

        painter.save()
        super().paintSection(painter, rect, logicalIndex)
        painter.restore()

        if logicalIndex == 0:
            style = self.style()
            # 2. Проверяем наличие стиля
            if style is None:
                return

            option = QStyleOptionButton()
            # Исправлена ошибка в кавычках adjusted
            option.rect = rect.adjusted(5, 5, -5, -5)
            option.state = (
                QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
            )

            if self.is_checked:
                option.state |= QStyle.StateFlag.State_On
            else:
                option.state |= QStyle.StateFlag.State_Off

            style.drawControl(QStyle.ControlElement.CE_CheckBox, option, painter)

    def mousePressEvent(self, e: QtGui.QMouseEvent | None) -> None:
        if e is None:
            super().mousePressEvent(e)
            return

        if self.logicalIndexAt(e.pos()) == 0:
            self.is_checked = not self.is_checked
            self.updateSection(0)

            model = self.model()
            if isinstance(model, CityTableModel):
                model.selectAll(self.is_checked)
        else:
            super().mousePressEvent(e)


class CityTableModel(QAbstractTableModel):
    def __init__(self, cities: list[City]) -> None:
        super().__init__()
        self.cities = cities
        self.headers = [
            "",
            "Город",
            "Регион",
            "Широта",
            "Долгота",  # Исправлено с "Высота" на "Долгота" для колонки 4
            "Timezone",
            "Высота ASL",
            "Данные заката",
        ]
        self.checked_states = [False] * len(cities)
        self.status_overrides = {}
        self._updating = False

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.cities)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        base_flags = super().flags(index)
        if index.column() == 0:
            return base_flags | Qt.ItemFlag.ItemIsUserCheckable
        if index.column() == 7:  # Колонка с кнопками
            return Qt.ItemFlag.ItemIsEnabled
        return base_flags | Qt.ItemFlag.ItemIsEditable

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        # Роли для делегата StatusActionDelegate
        if role == StatusActionDelegate.ViewEnabledRole:
            city = self.cities[index.row()]
            if (
                self.cities[index.row()].sunset_data.hash_before_edit
                and city.get_stable_hash() == city.sunset_data.hash_before_edit
            ):
                return True
            return False

        if role == StatusActionDelegate.UpdateEnabledRole:
            city = self.cities[index.row()]
            if (
                city.get_stable_hash() != city.sunset_data.hash_before_edit
                or city.sunset_data.source == Source.EDITED
            ):
                return True
            return False

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            return (
                Qt.CheckState.Checked
                if self.checked_states[index.row()]
                else Qt.CheckState.Unchecked
            )

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if index.column() == 0:
                return None

            city = self.cities[index.row()]
            col = index.column()
            if col == 1:
                return city.name
            if col == 2:
                return city.region
            if col == 3:
                return str(city.lat)
            if col == 4:
                return str(city.lon)
            if col == 5:
                return city.timezone
            if col == 6:
                return str(city.elevation)
            if col == 7:
                row = index.row()
                if row in self.status_overrides:
                    return self.status_overrides[row]

                city = self.cities[row]
                if city.get_stable_hash() != city.sunset_data.hash_before_edit:
                    return "❗️ Неактуальные данные"
                else:
                    if city.sunset_data.source == Source.CALCULATED:
                        return "✅ Загружено"
                    elif city.sunset_data.source == Source.EDITED:
                        return "⚠️ Изменено"

        return None

    def setData(
        self,
        index: QModelIndex,
        value: typing.Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if not index.isValid():
            return False

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            self.checked_states[index.row()] = value == Qt.CheckState.Checked.value
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            return True

        if role == Qt.ItemDataRole.EditRole:
            city = self.cities[index.row()]
            col = index.column()

            try:
                if col == 1:
                    city.name = value
                elif col == 2:
                    city.region = value
                elif col == 3:
                    city.lat = float(value.replace(",", "."))
                elif col == 4:
                    city.lon = float(value.replace(",", "."))
                elif col == 5:
                    city.timezone = value
                elif col == 6:
                    city.elevation = int(value)
                elif col == 7:
                    self.status_overrides[index.row()] = str(value)

                # Обновляем все затронутые роли
                self.dataChanged.emit(
                    index,
                    index,
                    [
                        Qt.ItemDataRole.DisplayRole,
                        StatusActionDelegate.UpdateEnabledRole,
                    ],
                )
                return True
            except ValueError:
                return False
        return False

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

    def addCity(self, city):
        last_row = len(self.cities)

        self.beginInsertRows(QModelIndex(), last_row, last_row)
        self.cities.append(city)
        self.checked_states.append(False)
        self.endInsertRows()

    def selectAll(self, state: bool) -> None:
        self.checked_states = [state] * len(self.cities)
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(len(self.cities) - 1, 0),
            [Qt.ItemDataRole.CheckStateRole],
        )

    def removeCheckedCities(self):
        indices_to_remove = [i for i, val in enumerate(self.checked_states) if val]
        indices_to_remove.sort(reverse=True)

        for row in indices_to_remove:
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.cities[row]
            del self.checked_states[row]
            self.endRemoveRows()

    def updateCheckedCities(self, year: int, weekday1: int, weekday2: int):
        indices_to_update = [i for i, val in enumerate(self.checked_states) if val]

        for row in indices_to_update:
            city = self.cities[row]
            city.sunset_data = get_city_sunset(city, year, weekday1, weekday2)
            city.sunset_data.hash_before_edit = city.get_stable_hash()
            if row in self.status_overrides:
                del self.status_overrides[row]

        if indices_to_update:
            for row in indices_to_update:
                top_left = self.index(row, 7)
                bottom_right = self.index(row, 7)
                self.dataChanged.emit(
                    top_left,
                    bottom_right,
                    [
                        Qt.ItemDataRole.DisplayRole,
                        StatusActionDelegate.UpdateEnabledRole,
                        StatusActionDelegate.ViewEnabledRole,
                    ],
                )
        return indices_to_update

    def handleButtonClick(self, row: int, action: str):
        """Обработчик кликов от делегата"""
        if action == "view":
            # Логика просмотра
            city = self.cities[row]
            print(f"Просмотр города: {city.name}")
            # Здесь можно открыть диалог просмотра

        elif action == "update":
            # Логика обновления
            city = self.cities[row]
            if city.get_stable_hash() != city.sunset_data.hash_before_edit:
                # Обновляем только один город
                city.sunset_data = get_city_sunset(
                    city, 2024, 1, 2
                )  # С параметрами по умолчанию
                if row in self.status_overrides:
                    del self.status_overrides[row]

                # Обновляем отображение
                index = self.index(row, 7)
                self.dataChanged.emit(
                    index,
                    index,
                    [
                        Qt.ItemDataRole.DisplayRole,
                        StatusActionDelegate.UpdateEnabledRole,
                    ],
                )
