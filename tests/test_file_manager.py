def test_load_from_json_successful_loading():
    """
    Проверка, что функция возвращает ожидаемую структуру данных
    """
    # Проверить, что функция возвращает ожидаемую структуру данных
    # Проверить типы данных (dict, list и т.д.)
    # Проверить, что данные соответствуют ожидаемым значениям
    pass


def test_load_from_json_file_not_found():
    """
    Проверка, как реагирует функция если файла не существует
    """
    # Проверить обработку FileNotFoundError
    pass


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
