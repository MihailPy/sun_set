from unittest.mock import Mock, patch

from PyQt6.QtWidgets import QMessageBox

from sun_set.services.dialog_service import (
    ask_retry,
    choose_directory,
    choose_file,
    choose_save_file,
    show_error,
    show_information,
    show_warning,
)


@patch("sun_set.services.dialog_service.QMessageBox.warning")
def test_show_warning(mock_warning):
    parent = Mock()

    show_warning(parent, "Title", "Message")

    mock_warning.assert_called_once_with(parent, "Title", "Message")


@patch("sun_set.services.dialog_service.QMessageBox.information")
def test_show_information(mock_information):
    parent = Mock()

    show_information(parent, "Title", "Message")

    mock_information.assert_called_once_with(parent, "Title", "Message")


@patch("sun_set.services.dialog_service.QMessageBox.critical")
def test_show_error(mock_critical):
    parent = Mock()

    show_error(parent, "Title", "Message")

    mock_critical.assert_called_once_with(parent, "Title", "Message")


@patch("sun_set.services.dialog_service.QMessageBox.question")
def test_ask_retry_returns_true_for_retry(mock_question):
    parent = Mock()
    mock_question.return_value = QMessageBox.StandardButton.Retry

    assert ask_retry(parent, "Title", "Message") is True


@patch("sun_set.services.dialog_service.QMessageBox.question")
def test_ask_retry_returns_false_for_cancel(mock_question):
    parent = Mock()
    mock_question.return_value = QMessageBox.StandardButton.Cancel

    assert ask_retry(parent, "Title", "Message") is False


@patch("sun_set.services.dialog_service.QFileDialog.getOpenFileName")
def test_choose_file(mock_get_open_file_name):
    mock_get_open_file_name.return_value = ("cities.json", "JSON Files (*.json)")

    result = choose_file(
        parent=Mock(),
        title="Выберите файл",
        file_filter="JSON Files (*.json)",
    )

    assert result == "cities.json"


@patch("sun_set.services.dialog_service.QFileDialog.getSaveFileName")
def test_choose_save_file(mock_get_save_file_name):
    mock_get_save_file_name.return_value = ("cities.json", "JSON Files (*.json)")

    result = choose_save_file(
        parent=Mock(),
        title="Сохранить файл",
        file_filter="JSON Files (*.json)",
    )

    assert result == "cities.json"


@patch("sun_set.services.dialog_service.QFileDialog.getExistingDirectory")
def test_choose_directory(mock_get_existing_directory):
    mock_get_existing_directory.return_value = "exports"

    result = choose_directory(
        parent=Mock(),
        title="Выберите папку",
    )

    assert result == "exports"
