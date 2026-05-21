class ImageExportError(Exception):
    """Base error for image export."""


class ExportSettingsError(ImageExportError):
    """Invalid export settings."""


class MissingMonthLayoutError(ImageExportError):
    """Layout settings for month are missing."""


class TemplateNotFoundError(ImageExportError):
    """Template image file was not found."""


class FontNotFoundError(ImageExportError):
    """Font file was not found."""


def get_user_friendly_error(error: Exception) -> str:
    if isinstance(error, TemplateNotFoundError):
        return "Файл шаблона не найден."

    if isinstance(error, FontNotFoundError):
        return "Файл шрифта не найден."

    if isinstance(error, MissingMonthLayoutError):
        return "В настройках расположения нет координат для одного из месяцев."

    if isinstance(error, ExportSettingsError):
        return "Ошибка в JSON-настройках экспорта."

    if isinstance(error, ImageExportError):
        return str(error)

    return "Не удалось выполнить экспорт изображения."
