from pathlib import Path

from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget


def show_warning(
    parent: QWidget,
    title: str,
    message: str,
) -> None:
    QMessageBox.warning(
        parent,
        title,
        message,
    )


def show_information(
    parent: QWidget,
    title: str,
    message: str,
) -> None:
    QMessageBox.information(
        parent,
        title,
        message,
    )


def show_error(
    parent: QWidget,
    title: str,
    message: str,
) -> None:
    QMessageBox.critical(
        parent,
        title,
        message,
    )


def ask_retry(
    parent: QWidget,
    title: str,
    message: str,
) -> bool:
    result = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel,
        QMessageBox.StandardButton.Retry,
    )

    return result == QMessageBox.StandardButton.Retry


def choose_file(
    parent: QWidget,
    title: str,
    file_filter: str,
    initial_path: str = "",
) -> str:
    file_path, _ = QFileDialog.getOpenFileName(
        parent,
        title,
        initial_path,
        file_filter,
    )
    return file_path


def choose_directory(
    parent: QWidget,
    title: str,
    initial_path: str = "",
) -> str:
    return QFileDialog.getExistingDirectory(
        parent,
        title,
        initial_path,
    )


def choose_save_file(
    parent: QWidget,
    title: str,
    file_filter: str,
    initial_path: str = "",
) -> str:
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        title,
        initial_path,
        file_filter,
    )
    return file_path


def ask_open_folder_after_export(
    parent: QWidget,
    message: str,
) -> bool:
    message_box = QMessageBox(parent)
    message_box.setWindowTitle("Экспорт изображений")
    message_box.setText(message)
    message_box.setIcon(QMessageBox.Icon.Information)

    open_folder_button = message_box.addButton(
        "Открыть папку",
        QMessageBox.ButtonRole.ActionRole,
    )
    message_box.addButton(QMessageBox.StandardButton.Ok)

    message_box.exec()

    return message_box.clickedButton() == open_folder_button


def open_directory(path: Path) -> None:
    QDesktopServices.openUrl(QUrl.fromLocalFile(str(path)))


def ask_save_discard_cancel(
    parent: QWidget,
    title: str,
    message: str,
) -> QMessageBox.StandardButton:
    return QMessageBox.question(
        parent,
        title,
        message,
        (
            QMessageBox.StandardButton.Save
            | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel
        ),
        QMessageBox.StandardButton.Save,
    )


def ask_confirmation(
    parent: QWidget,
    title: str,
    message: str,
) -> bool:
    result = QMessageBox.question(
        parent,
        title,
        message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )

    return result == QMessageBox.StandardButton.Yes
