from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QLineEdit, QStyledItemDelegate


class CityDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        col = index.column()

        # Настраиваем валидаторы в зависимости от колонки
        if col in (3, 4):  # Широта и Долгота (float)
            validator = QDoubleValidator(parent)
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            editor.setValidator(validator)
        elif col == 6:  # Высота ASL (int)
            validator = QIntValidator(parent)
            editor.setValidator(validator)

        return editor
