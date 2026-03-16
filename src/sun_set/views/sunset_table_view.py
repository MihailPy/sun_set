from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)

from sun_set.models.city import City
from sun_set.models.sunset import Source


class YearEditorWindow(QWidget):
    def __init__(self, city: City):
        super().__init__()
        self.city = city
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(
            f"Данные города {self.city.name} за {str(self.city.sunset_data.year)} год"
        )

        self.resize(600, 500)

        layout = QVBoxLayout()

        # Создаем вкладки для месяцев
        self.tabs = QTabWidget()

        if self.city.sunset_data.months:
            for month_info in self.city.sunset_data.months:
                tab = self.create_month_tab(month_info)
                month_name = self.get_month_name(month_info.month)
                self.tabs.addTab(tab, month_name)

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def create_month_tab(self, month_data):
        widget = QWidget()
        layout = QVBoxLayout()

        # Создаем таблицу: Строки = кол-во дней, Колонки = 3 (День, Неделя, Время)
        table = QTableWidget(len(month_data.days), 3)
        table.setHorizontalHeaderLabels(["Число", "День недели", "Время заката"])

        days_of_week = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]

        for row, entry in enumerate(month_data.days):
            # 1. Число (только для чтения)
            day_item = QTableWidgetItem(str(entry.day))
            day_item.setFlags(day_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 2. День недели (только для чтения)
            weekday_item = QTableWidgetItem(days_of_week[entry.weekday])
            weekday_item.setFlags(weekday_item.flags() & ~Qt.ItemFlag.ItemIsEditable)

            # 3. Время (РЕДАКТИРУЕМОЕ)
            time_item = QTableWidgetItem(entry.time)
            if entry.source == Source.EDITED:
                time_item.setBackground(QColor(255, 255, 200))
                time_item.setForeground(QColor(0, 0, 0))

            table.setItem(row, 0, day_item)
            table.setItem(row, 1, weekday_item)
            table.setItem(row, 2, time_item)

        # Растягиваем колонки
        table.horizontalHeader().setStretchLastSection(False)

        layout.addWidget(table)
        widget.setLayout(layout)

        # Сохраняем ссылку на таблицу в данные месяца, чтобы потом считать изменения
        # (Опционально, зависит от того, как ты планируешь сохранять)
        table.itemChanged.connect(lambda item: self.on_cell_changed(item, month_data))

        return widget

    def on_cell_changed(self, item, month_data):
        # Если изменили колонку с временем (индекс 2)
        if item.column() == 2:
            row = item.row()
            new_time = item.text()
            if new_time != month_data.days[row].time:
                # Обновляем объект данных напрямую
                month_data.days[row].time = new_time
                month_data.days[row].source = Source.EDITED
                self.city.sunset_data.source = Source.EDITED
                item.setBackground(QColor(255, 255, 200))
                item.setForeground(QColor(0, 0, 0))
                print(
                    f"Обновлено: {month_data.month} месяц, день {month_data.days[row].day} -> {new_time}"
                )

    def get_month_name(self, n):
        months = [
            "Январь",
            "Февраль",
            "Март",
            "Апрель",
            "Май",
            "Июнь",
            "Июль",
            "Август",
            "Сентябрь",
            "Октябрь",
            "Ноябрь",
            "Декабрь",
        ]
        return months[n - 1]
