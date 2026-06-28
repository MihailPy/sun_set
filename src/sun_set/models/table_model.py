from typing import Any

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

from sun_set.models.city import City
from sun_set.models.sunset import Source

STATUS_COLUMN = 7
SUNSET_DATA_COLUMN = 8


class SunsetDataActionDelegate(QStyledItemDelegate):
    buttonClicked = pyqtSignal(int)

    BTN_WIDTH = 90
    MARGIN = 5

    def sizeHint(self, option, index) -> QSize:
        return QSize(self.BTN_WIDTH + self.MARGIN * 2, 40)

    def paint(self, painter, option, index):
        if painter is None:
            return

        painter.save()

        button_rect = QRect(
            option.rect.left() + self.MARGIN,
            option.rect.top() + self.MARGIN,
            option.rect.width() - self.MARGIN * 2,
            option.rect.height() - self.MARGIN * 2,
        )

        button_option = QStyleOptionButton()
        button_option.rect = button_rect
        button_option.text = "Открыть"
        button_option.state = (
            QStyle.StateFlag.State_Enabled | QStyle.StateFlag.State_Active
        )

        style = option.widget.style() if option.widget else QApplication.style()
        if style:
            style.drawControl(
                QStyle.ControlElement.CE_PushButton,
                button_option,
                painter,
            )

        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:
        if event is None:
            return False

        if event.type() == QEvent.Type.MouseButtonRelease:
            if isinstance(event, QMouseEvent):
                pos = event.position().toPoint()

                button_rect = QRect(
                    option.rect.left() + self.MARGIN,
                    option.rect.top() + self.MARGIN,
                    option.rect.width() - self.MARGIN * 2,
                    option.rect.height() - self.MARGIN * 2,
                )

                if button_rect.contains(pos):
                    self.buttonClicked.emit(index.row())
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
            return

        if self.logicalIndexAt(e.pos()) == 0:
            self.is_checked = not self.is_checked
            self.updateSection(0)

            model = self.model()
            if isinstance(model, CityTableModel):
                model.select_all(self.is_checked)
        else:
            super().mousePressEvent(e)


class CityTableModel(QAbstractTableModel):
    selection_changed = pyqtSignal()

    def __init__(self, cities: list[City]) -> None:
        super().__init__()
        self.cities = cities
        self.headers = [
            "",
            "Город",
            "Регион",
            "Широта",
            "Долгота",
            "Timezone",
            "Высота ASL",
            "Статус",
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
        if index.column() in (STATUS_COLUMN, SUNSET_DATA_COLUMN):
            return Qt.ItemFlag.ItemIsEnabled
        return base_flags | Qt.ItemFlag.ItemIsEditable

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()
        city = self.cities[row]

        if role == Qt.ItemDataRole.CheckStateRole and col == 0:
            return (
                Qt.CheckState.Checked
                if self.checked_states[row]
                else Qt.CheckState.Unchecked
            )

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if col == 0:
                return None

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
            if col == STATUS_COLUMN:
                if row in self.status_overrides:
                    return self.status_overrides[row]

                if city.get_stable_hash() != city.sunset_data.hash_before_edit:
                    return "❗️ Неактуальные данные"
                else:
                    if city.sunset_data.source == Source.CALCULATED:
                        return "✅ Загружено"
                    elif city.sunset_data.source == Source.EDITED:
                        return "⚠️ Изменено"
            if col == SUNSET_DATA_COLUMN:
                return "Открыть"

        return None

    def setData(
        self,
        index: QModelIndex,
        value: Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if not index.isValid():
            return False

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == 0:
            if isinstance(value, Qt.CheckState):
                is_checked = value == Qt.CheckState.Checked
            else:
                is_checked = value == Qt.CheckState.Checked.value

            self.checked_states[index.row()] = is_checked
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            self.selection_changed.emit()
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
                elif col == STATUS_COLUMN:
                    self.status_overrides[index.row()] = str(value)

                # Обновляем все затронутые роли
                self.dataChanged.emit(
                    index,
                    index,
                    [
                        Qt.ItemDataRole.DisplayRole,
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

    def add_city(self, city):
        last_row = len(self.cities)

        self.beginInsertRows(QModelIndex(), last_row, last_row)
        self.cities.append(city)
        self.checked_states.append(False)
        self.endInsertRows()

    def select_all(self, state: bool) -> None:
        self.checked_states = [state] * len(self.cities)
        self.dataChanged.emit(
            self.index(0, 0),
            self.index(len(self.cities) - 1, 0),
            [Qt.ItemDataRole.CheckStateRole],
        )
        self.selection_changed.emit()

    def get_selected_cities(self) -> list[City] | None:
        selected_state_indices = [i for i, val in enumerate(self.checked_states) if val]
        if len(selected_state_indices) > 0:
            return [self.cities[i] for i in selected_state_indices]
        return None

    def remove_checked_cities(self):
        indices_to_remove = [i for i, val in enumerate(self.checked_states) if val]
        indices_to_remove.sort(reverse=True)

        for row in indices_to_remove:
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.cities[row]
            del self.checked_states[row]
            self.endRemoveRows()

    def clear_status_overrides_for_cities(self, cities: list[City]) -> None:
        for row, city in enumerate(self.cities):
            if city in cities and row in self.status_overrides:
                del self.status_overrides[row]

    def refresh_status_column(self) -> None:
        if not self.cities:
            return

        self.dataChanged.emit(
            self.index(0, STATUS_COLUMN),
            self.index(len(self.cities) - 1, STATUS_COLUMN),
            [
                Qt.ItemDataRole.DisplayRole,
            ],
        )

    def refresh_status_row(self, row: int) -> None:
        if row in self.status_overrides:
            del self.status_overrides[row]

        index = self.index(row, STATUS_COLUMN)
        self.dataChanged.emit(
            index,
            index,
            [
                Qt.ItemDataRole.DisplayRole,
            ],
        )

    def update_status_for_row(self, row: int) -> None:
        city = self.cities[row]

        if city.get_stable_hash() != city.sunset_data.hash_before_edit:
            self.status_overrides[row] = "❗️ Неактуальные данные"
        elif city.sunset_data.source == Source.CALCULATED:
            self.status_overrides[row] = "✅ Загружено"
        elif city.sunset_data.source == Source.EDITED:
            self.status_overrides[row] = "⚠️ Изменено"

        self.refresh_status_row(row)
