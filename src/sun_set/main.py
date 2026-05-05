import sys

from PyQt6.QtWidgets import QApplication

from sun_set.views.main_view import MainWindow


def create_app():
    """Инициализирует приложение и окно."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app, window


def main():
    """Точка входа в приложение."""
    app, window = create_app()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
