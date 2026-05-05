from unittest.mock import MagicMock, patch

import pytest

from sun_set.main import create_app, main


def test_create_app():
    """Проверяем создание объектов. Используем путь импорта как в main.py."""
    # ПАТЧИМ ТАМ, ГДЕ ИМПОРТИРУЕМ (внутри main_app_file)
    with (
        patch("sun_set.main.QApplication"),
        patch("sun_set.main.MainWindow") as MockWindow,
    ):
        # Создаем экземпляр-пустышку для возврата
        mock_instance = MagicMock()
        MockWindow.return_value = mock_instance

        app, window = create_app()

        # Проверка создания
        MockWindow.assert_called_once()
        # Чтобы Pyright не ругался, обращаемся к mock_instance явно
        mock_instance.show.assert_called_once()

        assert app is not None
        assert window == mock_instance


def test_main_execution():
    """Проверяем запуск основного цикла."""
    # Патчим create_app внутри того же модуля
    with (
        patch("sun_set.main.create_app") as mock_create,
        patch("sys.exit") as mock_exit,
    ):
        mock_app = MagicMock()
        mock_window = MagicMock()
        mock_create.return_value = (mock_app, mock_window)
        mock_app.exec.return_value = 0

        main()

        mock_create.assert_called_once()
        mock_app.exec.assert_called_once()
        mock_exit.assert_called_with(0)


@pytest.mark.parametrize("exit_code", [0, 1])
def test_sys_exit_code(exit_code):
    """Проверяем, что код выхода из app.exec передается в sys.exit."""
    with (
        patch("sun_set.main.create_app") as mock_create,
        patch("sys.exit") as mock_exit,
    ):
        mock_app = MagicMock()
        mock_app.exec.return_value = exit_code
        mock_create.return_value = (mock_app, MagicMock())

        main()

        mock_exit.assert_called_with(exit_code)
