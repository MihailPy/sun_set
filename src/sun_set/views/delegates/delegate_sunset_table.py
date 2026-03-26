from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from PyQt6.QtWidgets import QLineEdit, QStyledItemDelegate


class TimeDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)

        # Проверка что цифры не выходят за диапазон времени
        time_re = QRegularExpression(r"^([0-1]?[0-9]|2[0-3]):([0-5][0-9])$")
        validator = QRegularExpressionValidator(time_re, parent)
        editor.setValidator(validator)

        return editor
