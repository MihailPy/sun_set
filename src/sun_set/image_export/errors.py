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
