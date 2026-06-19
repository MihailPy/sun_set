from unittest.mock import Mock, patch

from PIL import Image

from sun_set.services.image_export_workflow import (
    build_selected_city_preview_image,
    export_selected_city_images,
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

    actual_results = export_selected_city_images(
        cities=cities,
        settings_path=settings_path,
        output_dir=output_dir,
    )

    assert actual_results == results
    mock_export_cities_images.assert_called_once_with(
        cities=cities,
        settings_path=settings_path,
        output_dir=output_dir,
    )
    mock_save_export_report.assert_called_once_with(results, output_dir)


@patch("sun_set.services.image_export_workflow.build_city_image_preview")
def test_build_selected_city_preview_image(mock_build_city_image_preview, tmp_path):
    city = Mock()
    settings_path = tmp_path / "settings.json"
    image = Mock(spec=Image.Image)

    mock_build_city_image_preview.return_value = image

    result = build_selected_city_preview_image(
        city=city,
        settings_path=settings_path,
    )

    assert result == image
    mock_build_city_image_preview.assert_called_once_with(
        city=city,
        settings_path=settings_path,
    )
