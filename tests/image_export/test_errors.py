from sun_set.image_export.errors import (
    ExportSettingsError,
    get_user_friendly_error,
)


def test_get_user_friendly_error_preserves_export_settings_message():
    error = ExportSettingsError("Файл настроек экспорта не является корректным JSON.")

    message = get_user_friendly_error(error)

    assert message == ("Файл настроек экспорта не является корректным JSON.")


def test_get_user_friendly_error_preserves_validation_message():
    error = ExportSettingsError("Image width must be greater than 0")

    message = get_user_friendly_error(error)

    assert message == "Image width must be greater than 0"
