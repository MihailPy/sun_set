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

from sun_set.models.city import City


class StatusActionDelegate(QStyledItemDelegate):
    buttonClicked = pyqtSignal(int)

    # Определим константы в одном месте
    BTN_WIDTH = 100
    MARGIN = 5

    def sizeHint(self, option, index) -> QSize:
        # 1. Считаем ширину текста
        status_text = f"{index.data() or 'Загружено'}"
        text_width = option.fontMetrics.horizontalAdvance(status_text)

        # 2. Итоговая ширина = текст + кнопка + отступы
        total_width = text_width + self.BTN_WIDTH + (self.MARGIN * 4)

        # 3. Высота (берем стандартную или чуть больше для кнопки)
        # base_size = super().sizeHint(option, index)
        return QSize(total_width, 40)

    def paint(self, painter, option, index):
        if painter is None:
            return
        self.initStyleOption(option, index)
        painter.save()
        v_margin = 1
        btn_rect = QRect(
            option.rect.right() - self.BTN_WIDTH - self.MARGIN,
            option.rect.top() + v_margin,
            self.BTN_WIDTH,
            option.rect.height() - 2 * v_margin,
        )

        text_rect = QRect(
            option.rect.left() + self.MARGIN,
            option.rect.top(),
            option.rect.width() - self.BTN_WIDTH - (self.MARGIN * 3),
            option.rect.height(),
        )

        status_text = f"{index.data() or 'Загружено'}"
        # AlignLeft гарантирует, что текст не "уедет" под кнопку
        painter.drawText(
            text_rect,
            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            status_text,
        )

        btn_option = QStyleOptionButton()
        btn_option.rect = btn_rect
        btn_option.text = "Просмотреть"
        # Добавляем State_Raised, это часто заставляет macOS рисовать объем
        btn_option.state = (
            QStyle.StateFlag.State_Enabled
            | QStyle.StateFlag.State_Active
            | QStyle.StateFlag.State_Raised
        )

        style = option.widget.style() if option.widget else QApplication.style()
        if style:
            # Сначала рисуем саму кнопку (рамку и фон)
            style.drawControl(QStyle.ControlElement.CE_PushButton, btn_option, painter)

        painter.restore()

    def editorEvent(self, event, model, option, index) -> bool:
        if event is None:
            return False

        if event.type() == QEvent.Type.MouseButtonRelease:
            if isinstance(event, QMouseEvent):
                # Используем ТЕ ЖЕ константы для проверки клика
                btn_rect = QRect(
                    option.rect.right() - self.BTN_WIDTH - self.MARGIN,
                    option.rect.top() + self.MARGIN,
                    self.BTN_WIDTH,
                    option.rect.height() - 2 * self.MARGIN,
                )

                if btn_rect.contains(event.position().toPoint()):
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
            "Высота",
            "Timezone",
            "Высота ASL",
            "Данные заката",
        ]
        self.checked_states = [False] * len(cities)

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.cities)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        base_flags = super().flags(index)
        if index.column() == 0:
            # Добавляем флаг именно здесь
            return base_flags | Qt.ItemFlag.ItemIsUserCheckable
        if index.column() == 7:
            return Qt.ItemFlag.ItemIsEnabled
        return base_flags | Qt.ItemFlag.ItemIsEditable

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

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
                    city.lat = float(value.replace(",", "."))  # Замена запятой на точку
                elif col == 4:
                    city.lon = float(value.replace(",", "."))
                elif col == 5:
                    city.timezone = value
                elif col == 6:
                    city.elevation = int(value)

                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return True
            except ValueError:
                # Здесь можно вызвать сигнал для статус-бара: "Ошибка формата данных"
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
        # Вычисляем индекс новой строки (обычно в конец)
        last_row = len(self.cities)

        # Уведомляем представление о начале вставки данных
        self.beginInsertRows(QModelIndex(), last_row, last_row)
        self.cities.append(city)
        self.checked_states.append(False)
        print(f"{self.checked_states}")
        self.endInsertRows()  # Завершаем вставку

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
