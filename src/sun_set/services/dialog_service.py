from PyQt6.QtWidgets import QMessageBox, QWidget


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
