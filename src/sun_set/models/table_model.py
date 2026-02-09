import typing

from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt

from sun_set.models.city import City


class CityTableModel(QAbstractTableModel):
    def __init__(self, cities: list[City]) -> None:
        super().__init__()
        self.cities = cities
        self.headers = ["Город", "Регион", "Широта", "Высота", "Timezone", "Высота ASL"]

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.cities)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self.headers)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        base_flags = super().flags(index)

        return base_flags | Qt.ItemFlag.ItemIsEditable

    def setData(
        self,
        index: QModelIndex,
        value: typing.Any,
        role: int = Qt.ItemDataRole.EditRole,
    ) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            # Убираем лишние пробелы
            value = value.strip() if isinstance(value, str) else value
            if (
                not value and index.column() <= 1
            ):  # Пример: название города не может быть пустым
                return False

            city = self.cities[index.row()]
            col = index.column()

            try:
                if col == 0:
                    city.name = value
                elif col == 1:
                    city.region = value
                elif col == 2:
                    city.lat = float(value.replace(",", "."))  # Замена запятой на точку
                elif col == 3:
                    city.lon = float(value.replace(",", "."))
                elif col == 4:
                    city.timezone = value
                elif col == 5:
                    city.elevation = int(value)

                self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole])
                return True
            except ValueError:
                # Здесь можно вызвать сигнал для статус-бара: "Ошибка формата данных"
                return False
        return False

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if role in (Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole):
            city = self.cities[index.row()]

            if index.column() == 0:
                return city.name
            if index.column() == 1:
                return city.region
            if index.column() == 2:
                return str(city.lat)
            if index.column() == 3:
                return str(city.lon)
            if index.column() == 4:
                return city.timezone
            if index.column() == 5:
                return str(city.elevation)
        return None

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
        self.endInsertRows()  # Завершаем вставку
