from typing import Any

from PyQt6 import QtGui
from PyQt6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    Qt,
    pyqtSignal,
)
from PyQt6.QtWidgets import (
    QHeaderView,
    QStyle,
    QStyleOptionButton,
)

from sun_set.models.city import City
from sun_set.models.sunset import Source

CHECK_COLUMN = 0
CITY_NAME_COLUMN = 1
REGION_COLUMN = 2
LAT_COLUMN = 3
LON_COLUMN = 4
TIMEZONE_COLUMN = 5
ELEVATION_COLUMN = 6
STATUS_COLUMN = 7
SUNSET_DATA_COLUMN = 8
CITY_TABLE_HEADERS = [
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


def build_city_sunset_status_text(city: City) -> str:
    if city.get_stable_hash() != city.sunset_data.hash_before_edit:
        return "Требует обновления"

    if city.sunset_data.source == Source.CALCULATED:
        return "Актуально"

    if city.sunset_data.source == Source.EDITED:
        return "Изменено вручную"

    if city.sunset_data.source == Source.ERROR_POLAR:
        return "Ошибка расчёта"

    return "Нет данных"


def can_open_city_sunset_data(city: City) -> bool:
    return bool(city.sunset_data.months)


class CityTableModel(QAbstractTableModel):
    selection_changed = pyqtSignal()

    def __init__(self, cities: list[City]) -> None:
        super().__init__()
        self.cities = cities
        self.headers = CITY_TABLE_HEADERS.copy()
        self.checked_states = [False] * len(cities)
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

        if role == Qt.ItemDataRole.TextAlignmentRole:
            if col in (STATUS_COLUMN, SUNSET_DATA_COLUMN):
                return Qt.AlignmentFlag.AlignCenter

        if role == Qt.ItemDataRole.CheckStateRole and col == CHECK_COLUMN:
            return (
                Qt.CheckState.Checked
                if self.checked_states[row]
                else Qt.CheckState.Unchecked
            )

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if col in (
                CITY_NAME_COLUMN,
                REGION_COLUMN,
                LAT_COLUMN,
                LON_COLUMN,
                TIMEZONE_COLUMN,
                ELEVATION_COLUMN,
            ):
                return self.get_city_cell_value(city, col)
            if col == STATUS_COLUMN:
                return build_city_sunset_status_text(city)
            if col == SUNSET_DATA_COLUMN:
                return "Открыть" if can_open_city_sunset_data(city) else ""

        if role == Qt.ItemDataRole.ForegroundRole:
            if col == SUNSET_DATA_COLUMN and can_open_city_sunset_data(city):
                return QtGui.QColor("#0066CC")

        if role == Qt.ItemDataRole.FontRole:
            if col == SUNSET_DATA_COLUMN and can_open_city_sunset_data(city):
                font = QtGui.QFont()
                font.setUnderline(True)
                return font

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
                if col == CITY_NAME_COLUMN:
                    city.name = value
                elif col == REGION_COLUMN:
                    city.region = value
                elif col == LAT_COLUMN:
                    city.lat = float(value.replace(",", "."))
                elif col == LON_COLUMN:
                    city.lon = float(value.replace(",", "."))
                elif col == TIMEZONE_COLUMN:
                    city.timezone = value
                elif col == ELEVATION_COLUMN:
                    city.elevation = int(value)

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
        index = self.index(row, STATUS_COLUMN)
        self.dataChanged.emit(
            index,
            index,
            [
                Qt.ItemDataRole.DisplayRole,
            ],
        )

    def update_status_for_row(self, row: int) -> None:

        self.refresh_status_row(row)

    def get_city_cell_value(self, city: City, col: int) -> str | None:
        if col == CITY_NAME_COLUMN:
            return city.name
        if col == REGION_COLUMN:
            return city.region
        if col == LAT_COLUMN:
            return str(city.lat)
        if col == LON_COLUMN:
            return str(city.lon)
        if col == TIMEZONE_COLUMN:
            return city.timezone
        if col == ELEVATION_COLUMN:
            return str(city.elevation)

        return None
