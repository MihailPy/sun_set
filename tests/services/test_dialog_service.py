from unittest.mock import Mock, patch

from PyQt6.QtWidgets import QMessageBox

from sun_set.services.dialog_service import (
    ask_open_folder_after_export,
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


@patch("sun_set.services.dialog_service.QMessageBox")
def test_ask_open_folder_after_export_returns_true(mock_message_box_class):
    parent = Mock()

    message_box = Mock()
    open_folder_button = Mock()

    mock_message_box_class.return_value = message_box
    message_box.addButton.side_effect = [open_folder_button, Mock()]
    message_box.clickedButton.return_value = open_folder_button

    result = ask_open_folder_after_export(parent, "Готово: 1")

    assert result is True
    message_box.setWindowTitle.assert_called_once_with("Экспорт изображений")
    message_box.setText.assert_called_once_with("Готово: 1")
    message_box.exec.assert_called_once()


@patch("sun_set.services.dialog_service.QMessageBox")
def test_ask_open_folder_after_export_returns_false(mock_message_box_class):
    parent = Mock()

    message_box = Mock()
    open_folder_button = Mock()
    ok_button = Mock()

    mock_message_box_class.return_value = message_box
    message_box.addButton.side_effect = [open_folder_button, ok_button]
    message_box.clickedButton.return_value = ok_button

    result = ask_open_folder_after_export(parent, "Готово: 1")

    assert result is False
