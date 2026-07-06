from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QLineEdit, QStyledItemDelegate

from sun_set.models.table_model import ELEVATION_COLUMN, LAT_COLUMN, LON_COLUMN


class CityDelegate(QStyledItemDelegate):
    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)
        col = index.column()

        if col in (LAT_COLUMN, LON_COLUMN):  # Широта и Долгота (float)
            validator = QDoubleValidator(parent)
            validator.setNotation(QDoubleValidator.Notation.StandardNotation)
            editor.setValidator(validator)
        elif col == ELEVATION_COLUMN:  # Высота ASL (int)
            validator = QIntValidator(parent)
            editor.setValidator(validator)

        return editor
