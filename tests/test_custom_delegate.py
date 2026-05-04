import pytest
from PyQt6.QtGui import QDoubleValidator, QIntValidator
from PyQt6.QtWidgets import QLineEdit, QTableWidget

from sun_set.views.delegates.custom_delegate import CityDelegate


@pytest.fixture
def table_setup(qtbot):
    table = QTableWidget(1, 7)
    delegate = CityDelegate()
    table.setItemDelegate(delegate)
    qtbot.addWidget(table)
    return table, delegate


def test_latitude_longitude_editor(table_setup):
    table, delegate = table_setup

    for col in (3, 4):
        index = table.model().index(0, col)
        editor = delegate.createEditor(table, None, index)

        assert isinstance(editor, QLineEdit)

        validator = editor.validator()
        assert isinstance(validator, QDoubleValidator)
        # Теперь Pyright знает, что у validator есть метод notation()
        assert validator.notation() == QDoubleValidator.Notation.StandardNotation


def test_altitude_editor(table_setup):
    table, delegate = table_setup
    index = table.model().index(0, 6)

    editor = delegate.createEditor(table, None, index)

    assert isinstance(editor, QLineEdit)
    assert isinstance(editor.validator(), QIntValidator)
