from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QLineEdit, QStyledItemDelegate


class CityDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        col = index.column()

        # Настраиваем валидаторы в зависимости от колонки
        if col in (2, 3):  # Широта и Долгота (float)
            validator = QDoubleValidator(parent)
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            editor.setValidator(validator)
        elif col == 5:  # Высота ASL (int)
            validator = QIntValidator(parent)
            editor.setValidator(validator)

        return editor
