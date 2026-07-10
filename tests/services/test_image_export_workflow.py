from unittest.mock import Mock, patch

from PIL import Image

from sun_set.image_export.errors import ImageExportError
from sun_set.services.image_export_workflow import (
    ImageExportErrorResult,
    ImageExportRequest,
    ImageExportSettingsLoadError,
    ImageExportSettingsLoadSuccess,
    ImageExportSuccessResult,
    ImagePreviewErrorResult,
    ImagePreviewRequest,
    ImagePreviewSuccessResult,
    build_image_export_result_message,
    build_selected_city_preview_image,
    create_default_image_export_settings,
    execute_image_export,
    execute_image_export_settings_load,
    execute_image_preview,
    export_selected_city_images,
    show_image_export_result_dialog,
)


@patch("sun_set.services.image_export_workflow.save_export_report")
@patch("sun_set.services.image_export_workflow.export_cities_images")
def test_export_selected_city_images(
    mock_export_cities_images,
    mock_save_export_report,
    tmp_path,
):
    cities = []
    settings_path = tmp_path / "settings.json"
    output_dir = tmp_path / "images"

    results = []
    mock_export_cities_images.return_value = results

    request = ImageExportRequest(
        cities=cities,
        settings_path=settings_path,
        output_dir=output_dir,
    )

    actual_results = export_selected_city_images(request)

    assert actual_results == results
    mock_export_cities_images.assert_called_once_with(
        cities=request.cities,
        settings_path=request.settings_path,
        output_dir=request.output_dir,
    )
    mock_save_export_report.assert_called_once_with(results, output_dir)


@patch("sun_set.services.image_export_workflow.build_city_image_preview")
def test_build_selected_city_preview_image(mock_build_city_image_preview, tmp_path):
    city = Mock()
    settings_path = tmp_path / "settings.json"
    image = Mock(spec=Image.Image)

    request = ImagePreviewRequest(
        city=city,
        settings_path=settings_path,
    )

    mock_build_city_image_preview.return_value = image

    result = build_selected_city_preview_image(request)

    assert result == image
    mock_build_city_image_preview.assert_called_once_with(
        city=request.city,
        settings_path=request.settings_path,
    )


@patch("sun_set.services.image_export_workflow.build_export_summary_message")
def test_build_image_export_result_message(mock_build_export_summary_message):
    results = []
    mock_build_export_summary_message.return_value = "Готово: 0\nОшибки: 0"

    message = build_image_export_result_message(results)

    assert message == "Готово: 0\nОшибки: 0"
    mock_build_export_summary_message.assert_called_once_with(results)


@patch("sun_set.services.image_export_workflow.open_directory")
@patch("sun_set.services.image_export_workflow.ask_open_folder_after_export")
@patch("sun_set.services.image_export_workflow.build_image_export_result_message")
def test_show_image_export_result_dialog_opens_folder(
    mock_build_message,
    mock_ask_open_folder,
    mock_open_directory,
    tmp_path,
):
    parent = Mock()
    results = []
    output_dir = tmp_path

    mock_build_message.return_value = "Готово: 0\nОшибки: 0"
    mock_ask_open_folder.return_value = True

    show_image_export_result_dialog(parent, results, output_dir)

    mock_ask_open_folder.assert_called_once_with(parent, "Готово: 0\nОшибки: 0")
    mock_open_directory.assert_called_once_with(output_dir)


@patch("sun_set.services.image_export_workflow.open_directory")
@patch("sun_set.services.image_export_workflow.ask_open_folder_after_export")
@patch("sun_set.services.image_export_workflow.build_image_export_result_message")
def test_show_image_export_result_dialog_does_not_open_folder(
    mock_build_message,
    mock_ask_open_folder,
    mock_open_directory,
    tmp_path,
):
    parent = Mock()
    results = []
    output_dir = tmp_path

    mock_build_message.return_value = "Готово: 0\nОшибки: 0"
    mock_ask_open_folder.return_value = False

    show_image_export_result_dialog(parent, results, output_dir)

    mock_open_directory.assert_not_called()


@patch("sun_set.services.image_export_workflow.export_selected_city_images")
def test_execute_image_export_success(mock_export_selected_city_images, tmp_path):
    request = ImageExportRequest(
        cities=[],
        settings_path=tmp_path / "settings.json",
        output_dir=tmp_path,
    )
    results = []

    mock_export_selected_city_images.return_value = results

    execution_result = execute_image_export(request)

    assert isinstance(execution_result, ImageExportSuccessResult)
    assert execution_result.results == results


@patch("sun_set.services.image_export_workflow.get_image_export_error_message")
@patch("sun_set.services.image_export_workflow.export_selected_city_images")
def test_execute_image_export_error(
    mock_export_selected_city_images,
    mock_get_image_export_error_message,
    tmp_path,
):
    request = ImageExportRequest(
        cities=[],
        settings_path=tmp_path / "settings.json",
        output_dir=tmp_path,
    )

    mock_export_selected_city_images.side_effect = RuntimeError("boom")
    mock_get_image_export_error_message.return_value = "Ошибка экспорта"

    execution_result = execute_image_export(request)

    assert isinstance(execution_result, ImageExportErrorResult)
    assert execution_result.error_message == "Ошибка экспорта"


@patch("sun_set.services.image_export_workflow.build_selected_city_preview_image")
def test_execute_image_preview_success(
    mock_build_selected_city_preview_image, tmp_path
):
    request = ImagePreviewRequest(
        city=Mock(),
        settings_path=tmp_path / "settings.json",
    )
    image = Mock(spec=Image.Image)

    mock_build_selected_city_preview_image.return_value = image

    execution_result = execute_image_preview(request)

    assert isinstance(execution_result, ImagePreviewSuccessResult)
    assert execution_result.image == image


@patch("sun_set.services.image_export_workflow.get_image_export_error_message")
@patch("sun_set.services.image_export_workflow.build_selected_city_preview_image")
def test_execute_image_preview_error(
    mock_build_selected_city_preview_image,
    mock_get_image_export_error_message,
    tmp_path,
):
    request = ImagePreviewRequest(
        city=Mock(),
        settings_path=tmp_path / "settings.json",
    )

    mock_build_selected_city_preview_image.side_effect = RuntimeError("boom")
    mock_get_image_export_error_message.return_value = "Ошибка предпросмотра"

    execution_result = execute_image_preview(request)

    assert isinstance(execution_result, ImagePreviewErrorResult)
    assert execution_result.error_message == "Ошибка предпросмотра"


@patch("sun_set.services.image_export_workflow.load_export_settings")
def test_execute_image_export_settings_load_success(
    mock_load_export_settings, tmp_path
):
    settings = Mock()
    settings_path = tmp_path / "settings.json"

    mock_load_export_settings.return_value = settings

    result = execute_image_export_settings_load(settings_path)

    assert isinstance(result, ImageExportSettingsLoadSuccess)
    assert result.settings == settings


@patch("sun_set.services.image_export_workflow.get_image_export_error_message")
@patch("sun_set.services.image_export_workflow.load_export_settings")
def test_execute_image_export_settings_load_image_export_error(
    mock_load_export_settings,
    mock_get_image_export_error_message,
    tmp_path,
):
    settings_path = tmp_path / "settings.json"
    error = ImageExportError("boom")

    mock_load_export_settings.side_effect = error
    mock_get_image_export_error_message.return_value = "Ошибка настроек"

    result = execute_image_export_settings_load(settings_path)

    assert isinstance(result, ImageExportSettingsLoadError)
    assert result.message == "Ошибка настроек"
    mock_get_image_export_error_message.assert_called_once_with(error)


@patch("sun_set.services.image_export_workflow.load_export_settings")
def test_execute_image_export_settings_load_unexpected_error(
    mock_load_export_settings,
    tmp_path,
):
    settings_path = tmp_path / "settings.json"

    mock_load_export_settings.side_effect = RuntimeError("Нет доступа")

    result = execute_image_export_settings_load(settings_path)

    assert isinstance(result, ImageExportSettingsLoadError)
    assert result.message == "Нет доступа"


@patch("sun_set.services.image_export_workflow.create_default_export_settings")
def test_create_default_image_export_settings(mock_create_default_export_settings):
    settings = Mock()
    mock_create_default_export_settings.return_value = settings

    result = create_default_image_export_settings()

    assert result == settings
    mock_create_default_export_settings.assert_called_once_with()
