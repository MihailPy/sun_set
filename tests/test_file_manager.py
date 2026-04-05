import json
from unittest.mock import mock_open, patch

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


@pytest.fixture
def months_data():
    months = [
        {
            "month": 1,
            "days": [
                {"day": 1, "weekday": 5, "time": "16:10", "source": 1},
                {"day": 7, "weekday": 4, "time": "16:18", "source": 1},
                {"day": 8, "weekday": 5, "time": "16:20", "source": 1},
                {"day": 14, "weekday": 4, "time": "16:30", "source": 1},
                {"day": 15, "weekday": 5, "time": "16:32", "source": 1},
                {"day": 21, "weekday": 4, "time": "16:43", "source": 1},
                {"day": 22, "weekday": 5, "time": "16:45", "source": 1},
                {"day": 28, "weekday": 4, "time": "16:58", "source": 1},
                {"day": 29, "weekday": 5, "time": "17:00", "source": 1},
            ],
        },
        {
            "month": 2,
            "days": [
                {"day": 4, "weekday": 4, "time": "17:13", "source": 1},
                {"day": 5, "weekday": 5, "time": "17:15", "source": 1},
                {"day": 11, "weekday": 4, "time": "17:28", "source": 1},
                {"day": 12, "weekday": 5, "time": "17:30", "source": 1},
                {"day": 18, "weekday": 4, "time": "17:43", "source": 1},
                {"day": 19, "weekday": 5, "time": "17:45", "source": 1},
                {"day": 25, "weekday": 4, "time": "17:58", "source": 1},
                {"day": 26, "weekday": 5, "time": "18:00", "source": 1},
            ],
        },
        {
            "month": 3,
            "days": [
                {"day": 4, "weekday": 4, "time": "18:13", "source": 1},
                {"day": 5, "weekday": 5, "time": "18:15", "source": 1},
                {"day": 11, "weekday": 4, "time": "18:27", "source": 1},
                {"day": 12, "weekday": 5, "time": "18:29", "source": 1},
                {"day": 18, "weekday": 4, "time": "18:41", "source": 1},
                {"day": 19, "weekday": 5, "time": "18:43", "source": 1},
                {"day": 25, "weekday": 4, "time": "18:56", "source": 1},
                {"day": 26, "weekday": 5, "time": "18:58", "source": 1},
            ],
        },
        {
            "month": 4,
            "days": [
                {"day": 1, "weekday": 4, "time": "19:10", "source": 1},
                {"day": 2, "weekday": 5, "time": "19:12", "source": 1},
                {"day": 8, "weekday": 4, "time": "19:24", "source": 1},
                {"day": 9, "weekday": 5, "time": "19:26", "source": 1},
                {"day": 15, "weekday": 4, "time": "19:38", "source": 1},
                {"day": 16, "weekday": 5, "time": "19:40", "source": 1},
                {"day": 22, "weekday": 4, "time": "19:52", "source": 1},
                {"day": 23, "weekday": 5, "time": "19:54", "source": 1},
                {"day": 29, "weekday": 4, "time": "20:06", "source": 1},
                {"day": 30, "weekday": 5, "time": "20:08", "source": 1},
            ],
        },
        {
            "month": 5,
            "days": [
                {"day": 6, "weekday": 4, "time": "20:20", "source": 1},
                {"day": 7, "weekday": 5, "time": "20:22", "source": 1},
                {"day": 13, "weekday": 4, "time": "20:34", "source": 1},
                {"day": 14, "weekday": 5, "time": "20:36", "source": 1},
                {"day": 20, "weekday": 4, "time": "20:47", "source": 1},
                {"day": 21, "weekday": 5, "time": "20:48", "source": 1},
                {"day": 27, "weekday": 4, "time": "20:58", "source": 1},
                {"day": 28, "weekday": 5, "time": "21:00", "source": 1},
            ],
        },
        {
            "month": 6,
            "days": [
                {"day": 3, "weekday": 4, "time": "21:08", "source": 1},
                {"day": 4, "weekday": 5, "time": "21:09", "source": 1},
                {"day": 10, "weekday": 4, "time": "21:15", "source": 1},
                {"day": 11, "weekday": 5, "time": "21:16", "source": 1},
                {"day": 17, "weekday": 4, "time": "21:20", "source": 1},
                {"day": 18, "weekday": 5, "time": "21:20", "source": 1},
                {"day": 24, "weekday": 4, "time": "21:21", "source": 1},
                {"day": 25, "weekday": 5, "time": "21:21", "source": 1},
            ],
        },
        {
            "month": 7,
            "days": [
                {"day": 1, "weekday": 4, "time": "21:20", "source": 1},
                {"day": 2, "weekday": 5, "time": "21:19", "source": 1},
                {"day": 8, "weekday": 4, "time": "21:14", "source": 1},
                {"day": 9, "weekday": 5, "time": "21:14", "source": 1},
                {"day": 15, "weekday": 4, "time": "21:07", "source": 1},
                {"day": 16, "weekday": 5, "time": "21:05", "source": 1},
                {"day": 22, "weekday": 4, "time": "20:56", "source": 1},
                {"day": 23, "weekday": 5, "time": "20:55", "source": 1},
                {"day": 29, "weekday": 4, "time": "20:44", "source": 1},
                {"day": 30, "weekday": 5, "time": "20:42", "source": 1},
            ],
        },
        {
            "month": 8,
            "days": [
                {"day": 5, "weekday": 4, "time": "20:30", "source": 1},
                {"day": 6, "weekday": 5, "time": "20:27", "source": 1},
                {"day": 12, "weekday": 4, "time": "20:14", "source": 1},
                {"day": 13, "weekday": 5, "time": "20:12", "source": 1},
                {"day": 19, "weekday": 4, "time": "19:58", "source": 1},
                {"day": 20, "weekday": 5, "time": "19:55", "source": 1},
                {"day": 26, "weekday": 4, "time": "19:40", "source": 1},
                {"day": 27, "weekday": 5, "time": "19:38", "source": 1},
            ],
        },
        {
            "month": 9,
            "days": [
                {"day": 2, "weekday": 4, "time": "19:22", "source": 1},
                {"day": 3, "weekday": 5, "time": "19:20", "source": 1},
                {"day": 9, "weekday": 4, "time": "19:04", "source": 1},
                {"day": 10, "weekday": 5, "time": "19:02", "source": 1},
                {"day": 16, "weekday": 4, "time": "18:46", "source": 1},
                {"day": 17, "weekday": 5, "time": "18:43", "source": 1},
                {"day": 23, "weekday": 4, "time": "18:27", "source": 1},
                {"day": 24, "weekday": 5, "time": "18:25", "source": 1},
                {"day": 30, "weekday": 4, "time": "18:09", "source": 1},
            ],
        },
        {
            "month": 10,
            "days": [
                {"day": 1, "weekday": 5, "time": "18:06", "source": 1},
                {"day": 7, "weekday": 4, "time": "17:51", "source": 1},
                {"day": 8, "weekday": 5, "time": "17:48", "source": 1},
                {"day": 14, "weekday": 4, "time": "17:33", "source": 1},
                {"day": 15, "weekday": 5, "time": "17:31", "source": 1},
                {"day": 21, "weekday": 4, "time": "17:16", "source": 1},
                {"day": 22, "weekday": 5, "time": "17:14", "source": 1},
                {"day": 28, "weekday": 4, "time": "17:00", "source": 1},
                {"day": 29, "weekday": 5, "time": "16:58", "source": 1},
            ],
        },
        {
            "month": 11,
            "days": [
                {"day": 4, "weekday": 4, "time": "16:45", "source": 1},
                {"day": 5, "weekday": 5, "time": "16:43", "source": 1},
                {"day": 11, "weekday": 4, "time": "16:32", "source": 1},
                {"day": 12, "weekday": 5, "time": "16:30", "source": 1},
                {"day": 18, "weekday": 4, "time": "16:20", "source": 1},
                {"day": 19, "weekday": 5, "time": "16:18", "source": 1},
                {"day": 25, "weekday": 4, "time": "16:10", "source": 1},
                {"day": 26, "weekday": 5, "time": "16:09", "source": 1},
            ],
        },
        {
            "month": 12,
            "days": [
                {"day": 2, "weekday": 4, "time": "16:04", "source": 1},
                {"day": 3, "weekday": 5, "time": "16:03", "source": 1},
                {"day": 9, "weekday": 4, "time": "16:00", "source": 1},
                {"day": 10, "weekday": 5, "time": "15:59", "source": 1},
                {"day": 16, "weekday": 4, "time": "15:59", "source": 1},
                {"day": 17, "weekday": 5, "time": "15:59", "source": 1},
                {"day": 23, "weekday": 4, "time": "16:02", "source": 1},
                {"day": 24, "weekday": 5, "time": "16:02", "source": 1},
                {"day": 30, "weekday": 4, "time": "16:08", "source": 1},
                {"day": 31, "weekday": 5, "time": "16:09", "source": 1},
            ],
        },
    ]
    return months


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
    assert isinstance(cities[0], City)

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


def test_load_from_json_permission_denied(tmp_path):
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
    assert error == "Ошибка: Не удалось разобрать JSON."


def test_load_from_directory_instead_of_file(tmp_path):
    """
    Проверка, поведения функции, если вместо пути к файлу, путь к папке
    """
    dir_path = tmp_path / "sub_directory"
    dir_path.mkdir()

    cities, error = load_from_json(dir_path)

    assert cities is None
    assert error == "Ошибка: Не удалось открыть файл, путь является папкой."


def test_load_from_json_invalid_json(tmp_path):
    """
    Проверка, некорректного json синтаксиса
    """
    bad_data = """
    [
        {
            "name": "Москва",
            "sunset_data": {
                "hash_before_edit": None,  # ОШИБКА: в JSON должно быть null
                "months": None,           # ОШИБКА: лишняя запятая и None
            }
        }
    ]
    """
    file = tmp_path / "bad_data.json"
    file.write_text(bad_data, encoding="utf-8")

    cities, error = load_from_json(str(file))

    assert cities is None
    assert error == "Ошибка: Не удалось разобрать JSON."


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


@pytest.mark.parametrize(
    "special_name",
    [
        "Москва\nСити",  # Перенос строки
        "Berlin\tDistrict",  # Табуляция
        'Quotes "quoted"',  # Двойные кавычки
        "Slash \\ backslash",  # Обратный слэш
        "Emoji 🌍🔥",  # Юникод и эмодзи
        "Symbols !@#$%^&*()",  # Спецсимволы
        "   Space test   ",  # Пробелы по краям
    ],
)
def test_load_from_json_special_characters(tmp_path, special_name, data_file):
    """
    Специальные символы в строках
    """
    data_file[0]["name"] = special_name

    file = tmp_path / "test_data.json"

    file.write_text(json.dumps(data_file))

    cities, error = load_from_json(str(file))

    assert cities is not None
    assert cities[0].name == special_name
    assert cities[0].sunset_data.hash_before_edit is None
    assert error is None


def test_load_from_json_deep_nesting(tmp_path, data_file, months_data):
    """
    Проверка, что функция загружает данные с глубокой вложенностью
    """
    data_file[0]["sunset_data"]["months"] = months_data
    data_file[0]["sunset_data"]["hash_before_edit"] = (
        "79983d577c9c688558f92e38e6e60d98cbd4419df4a4d93db293d027c7ad8963"
    )

    file = tmp_path / "test_data_deep_nesting.json"
    file.write_text(json.dumps(data_file))

    cities, error = load_from_json(str(file))

    assert cities is not None
    assert error is None

    assert cities[0].sunset_data.year == data_file[0]["sunset_data"]["year"]
    assert cities[0].sunset_data.hash_before_edit is not None

    assert cities[0].sunset_data.months is not None
    assert cities[0].sunset_data.months[0].days[0] is not None
    assert cities[0].sunset_data.months[0].days[0].time == "16:10"


def test_file_not_left_open(data_file):
    """
    Проверка, что функция корректно закрывает файл
    """
    json_input = json.dumps(data_file)

    m = mock_open(read_data=json_input)

    with patch("builtins.open", m):
        cities, error = load_from_json("fake_path.json")

    assert cities is not None and error is None

    m.assert_called_once_with("fake_path.json", encoding="utf-8")

    handle = m()
    handle.close.assert_called()


def test_load_from_json_type_error(tmp_path, data_file):
    """
    Проверка обработки TypeError при несовместимых типах данных
    """
    bad_data = data_file
    bad_data[0]["lat"] = "not_a_number"

    file = tmp_path / "type_error.json"
    file.write_text(json.dumps(bad_data))

    cities, error = load_from_json(str(file))

    assert cities is None
    assert error is not None
    assert "Ошибка в структуре данных файла" in error
    assert "float" in error.lower() or "lat" in error.lower()


def test_load_from_json_ignores_non_dict_items(tmp_path, data_file):
    """
    Проверка, что не-dict элементы игнорируются
    """
    data_file.append("not a dict")
    data_file.append(121)
    data_file.append(None)
    data_file.append(["another", "list"])

    file = tmp_path / "mixed.json"
    file.write_text(json.dumps(data_file))

    cities, error = load_from_json(str(file))

    assert error is None
    assert cities is not None
    assert len(cities) == 1
    assert cities[0].name == "Москва"


@pytest.mark.parametrize("key_to_remove", ["region", "timezone"])
def test_load_from_json_missing_required_fields(tmp_path, data_file, key_to_remove):
    """
    Проверка реакции на пропущенные обязательные поля
    """
    bad_data = data_file
    del bad_data[0][key_to_remove]

    file = tmp_path / "missing_fields.json"
    file.write_text(json.dumps(bad_data))

    cities, error = load_from_json(str(file))

    assert cities is None
    assert error is not None
    assert "Ошибка в структуре данных файла" in error


def test_load_from_json_empty_list(tmp_path):
    """
    Проверка обработки пустого списка в JSON
    """
    file = tmp_path / "empty_file.json"
    file.write_text("[]")

    cities, error = load_from_json(str(file))

    assert error is None
    assert cities == []
