import json

import pytest

from sun_set.api.file_manager import load_from_json
from sun_set.models.city import City


@pytest.fixture
def data_file():
    data = [
        {
            "name": "Москва",
            "region": "Moscow",
            "lat": 55.7558,
            "lon": 37.6173,
            "timezone": "Europe/Moscow",
            "elevation": 170,
            "sunset_data": {
                "year": 2033,
                "source": 1,
                "hash_before_edit": None,
                "months": None,
            },
        }
    ]
    return data


def test_load_from_json_successful_loading(tmp_path, data_file):
    """
    Проверка, что функция возвращает ожидаемую структуру данных
    """
    file = tmp_path / "cities.json"
    file.write_text(json.dumps(data_file))

    cities, error = load_from_json(str(file))

    assert error is None
    assert isinstance(cities, list)
    assert len(cities) == 1
    assert type(cities[0]) is City

    assert cities[0].name == "Москва"
    assert cities[0].lat == 55.7558
    assert cities[0].elevation == 170

    assert cities[0].sunset_data.year == 2033
    assert cities[0].sunset_data.hash_before_edit is None


def test_load_from_json_file_not_found():
    """
    Проверка, как реагирует функция если файла не существует
    """
    cities, error = load_from_json("nonexistent.txt")
    assert cities is None
    assert error == "Ошибка: Файл не найден. Проверьте путь к файлу."


def test_load_from_json_permission_defied(tmp_path):
    """
    Проверка, как реагирует функция если нет прав на чтения файла
    """
    file = tmp_path / "restricted.txt"
    file.write_text("top secret")

    # Лишаем прав на чтение (0o000)
    file.chmod(0o000)

    try:
        cities, error = load_from_json(str(file))

        assert cities is None
        assert error == "Ошибка: Нет прав доступа для чтения этого файла."

    finally:
        # Возвращаем права (0o666), чтобы файл смог быть удален
        file.chmod(0o666)


def test_load_from_json_empty_file(tmp_path):
    """
    Проверка, поведения функции, если файл пустой
    """
    empty_file = tmp_path / "empty.json"
    empty_file.write_text("")

    cities, error = load_from_json(str(empty_file))

    assert cities is None
    assert error == "Ошибка: Файл пустой, поврежден или имеет неверный формат JSON."


def test_load_from_directory_instead_of_file(tmp_path):
    """
    Проверка, поведения функции, если вместо пути к файлу, путь к папке
    """
    dir_path = tmp_path / "sub_directory"
    dir_path.mkdir()

    cities, error = load_from_json(dir_path)

    assert cities is None
    assert error == "Ошибка: Не удалось открыть файл, путь является папкой."


def test_load_from_json_invalid_json():
    """
    Проверка, некорректного json синтаксиса
    """
    # Проверить обработку JSONDecodeError
    # Пример: {"key": "value",} - лишняя запятая
    pass


def test_load_from_json_invalid_encoding(tmp_path, data_file):
    """
    Проверка, некорректной кодировки файла
    """
    file_path = tmp_path / "wrong_encoding.json"

    with open(file_path, "w", encoding="utf-16") as f:
        f.write(json.dumps(data_file))

    cities, error = load_from_json(str(file_path))

    assert cities is None
    assert error == "Ошибка: декодирования Unicode."


def test_load_from_json_special_characters():
    """
    Специальные символы в строках
    """
    # Юникод, эмодзи, управляющие последовательности


def test_load_from_json_deep_nesting():
    """
    Проверка, что функция загружает данные с глубокой вложенностью
    """
    # Проверить, что функция не падает при глубокой вложенности


def test_file_not_left_open():
    """
    Проверка, что функция корректно закрывает файл
    """
    # Использовать mock или проверить, что файловый дескриптор не остался открытым
