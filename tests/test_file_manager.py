import json

from sun_set.api.file_manager import load_from_json
from sun_set.models.city import City


def test_load_from_json_successful_loading(tmp_path):
    """
    Проверка, что функция возвращает ожидаемую структуру данных
    """
    file = tmp_path / "cities.json"
    data = [
        {
            "name": "Moscow",
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
    file.write_text(json.dumps(data))

    cities, error = load_from_json(str(file))

    assert error is None
    assert isinstance(cities, list)
    assert len(cities) == 1
    assert type(cities[0]) is City

    assert cities[0].name == "Moscow"
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


def test_load_from_json_permission_defied():
    """
    Проверка, как реагирует функция если нет прав на чтения файла
    """
    # Проверить обработку PermissionError
    pass


def test_load_from_json_empty_file():
    """
    Проверка, поведения функции, если файл пустой
    """
    # Проверить обработку JSONDecodeError
    pass


def test_load_from_directory_instead_of_file():
    """
    Проверка, поведения функции, если вместо пути к файлу, путь к папке
    """
    # Проверить обработку IsADirectoryError
    pass


def test_load_from_json_invalid_json():
    """
    Проверка, некорректного json синтаксиса
    """
    # Проверить обработку JSONDecodeError
    # Пример: {"key": "value",} - лишняя запятая
    pass


def test_load_from_json_invalid_encoding():
    """
    Проверка, некорректной кодировки файла
    """
    # Проверить обработку UnicodeDecodeError
    pass


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
