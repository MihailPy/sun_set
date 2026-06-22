from unittest.mock import Mock, patch

from PIL import Image

from sun_set.services.image_export_workflow import (
    ImageExportRequest,
    build_image_export_result_message,
    build_image_preview_request,
    build_selected_city_preview_image,
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

    mock_build_city_image_preview.return_value = image

    request = build_image_preview_request(
        city=city,
        settings_path=settings_path,
    )

    result = build_selected_city_preview_image(request)

    assert result == image
    mock_build_city_image_preview.assert_called_once_with(
        city=city,
        settings_path=settings_path,
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
