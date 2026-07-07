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
from sun_set.services.city_sunset_status_service import (
    build_city_sunset_status_text,
    can_open_city_sunset_data,
)

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
EDITABLE_CITY_COLUMNS = {
    CITY_NAME_COLUMN,
    REGION_COLUMN,
    LAT_COLUMN,
    LON_COLUMN,
    TIMEZONE_COLUMN,
    ELEVATION_COLUMN,
}


def is_editable_city_column(col: int) -> bool:
    return col in EDITABLE_CITY_COLUMNS


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

        if logicalIndex == CHECK_COLUMN:
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

        if self.logicalIndexAt(e.pos()) == CHECK_COLUMN:
            self.is_checked = not self.is_checked
            self.updateSection(0)

            model = self.model()
            if isinstance(model, CityTableModel):
                model.set_all_rows_selected(self.is_checked)
        else:
            super().mousePressEvent(e)


class CityTableModel(QAbstractTableModel):
    selection_changed = pyqtSignal()

    def __init__(self, cities: list[City]) -> None:
        super().__init__()
        self.cities = cities
        self.headers = CITY_TABLE_HEADERS.copy()
        self.selected_rows = [False] * len(cities)
        self._updating = False

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.cities)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        base_flags = super().flags(index)
        if index.column() == CHECK_COLUMN:
            return base_flags | Qt.ItemFlag.ItemIsUserCheckable
        if index.column() in (STATUS_COLUMN, SUNSET_DATA_COLUMN):
            return Qt.ItemFlag.ItemIsEnabled
        if is_editable_city_column(index.column()):
            return base_flags | Qt.ItemFlag.ItemIsEditable

        return base_flags

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
                if self.selected_rows[row]
                else Qt.CheckState.Unchecked
            )

        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            if is_editable_city_column(col):
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

        if role == Qt.ItemDataRole.CheckStateRole and index.column() == CHECK_COLUMN:
            if isinstance(value, Qt.CheckState):
                is_checked = value == Qt.CheckState.Checked
            else:
                is_checked = value == Qt.CheckState.Checked.value

            self.selected_rows[index.row()] = is_checked
            self.dataChanged.emit(index, index, [Qt.ItemDataRole.CheckStateRole])
            self.selection_changed.emit()
            return True

        if role == Qt.ItemDataRole.EditRole:
            city = self.cities[index.row()]
            col = index.column()

            if not is_editable_city_column(col):
                return False

            try:
                if not self.set_city_cell_value(city, col, value):
                    return False

                self.dataChanged.emit(
                    index,
                    index,
                    [Qt.ItemDataRole.DisplayRole],
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
        self.selected_rows.append(False)
        self.endInsertRows()

    def set_all_rows_selected(self, state: bool) -> None:
        self.selected_rows = [state] * len(self.cities)
        self.dataChanged.emit(
            self.index(0, CHECK_COLUMN),
            self.index(len(self.cities) - 1, CHECK_COLUMN),
            [Qt.ItemDataRole.CheckStateRole],
        )
        self.selection_changed.emit()

    def get_selected_cities(self) -> list[City] | None:
        selected_row_indexes = self.get_selected_row_indexes()

        if selected_row_indexes:
            return [self.cities[index] for index in selected_row_indexes]

        return None

    def remove_selected_cities(self):
        indices_to_remove = self.get_selected_row_indexes()
        indices_to_remove.sort(reverse=True)

        for row in indices_to_remove:
            self.beginRemoveRows(QModelIndex(), row, row)
            del self.cities[row]
            del self.selected_rows[row]
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

    def set_city_cell_value(self, city: City, col: int, value: Any) -> bool:
        if col == CITY_NAME_COLUMN:
            city.name = value
            return True
        if col == REGION_COLUMN:
            city.region = value
            return True
        if col == LAT_COLUMN:
            city.lat = float(value.replace(",", "."))
            return True
        if col == LON_COLUMN:
            city.lon = float(value.replace(",", "."))
            return True
        if col == TIMEZONE_COLUMN:
            city.timezone = value
            return True
        if col == ELEVATION_COLUMN:
            city.elevation = int(value)
            return True

        return False

    def get_selected_row_indexes(self) -> list[int]:
        return [index for index, selected in enumerate(self.selected_rows) if selected]
