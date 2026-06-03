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
