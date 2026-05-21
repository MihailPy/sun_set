# from pathlib import Path
import copy

from sun_set.core.astronomy import get_city_sunset
from sun_set.image_export.service import (
    build_output_filename,
    export_cities_images,
    export_city_image,
)


def test_export_city_image_creates_file(test_city, settings_path, tmp_path):
    output_path = tmp_path / "out.png"

    export_city_image(
        city=test_city,
        settings_path=settings_path,
        output_path=output_path,
    )

    assert output_path.exists()


def test_export_cities_images_creates_files(
    test_city,
    second_test_city,
    settings_path,
    tmp_path,
):
    output_dir = tmp_path / "out"

    results = export_cities_images(
        cities=[test_city, second_test_city],
        settings_path=settings_path,
        output_dir=output_dir,
    )

    assert len(results) == 2
    assert all(result.success for result in results)
    assert len(list(output_dir.glob("*.png"))) == 2


def test_build_output_filename():
    assert build_output_filename("New York", 2026) == "2026_New_York.png"


def test_export_cities_images_continues_after_city_error(
    test_city,
    settings_path,
    tmp_path,
):
    bad_city = copy.deepcopy(test_city)
    bad_city.name = "Bad City"

    bad_city.sunset_data = get_city_sunset(bad_city, 2024, 0, 1)
    # тут оставляем все 12 месяцев, а в settings есть только 1,2,3

    output_dir = tmp_path / "out"

    results = export_cities_images(
        cities=[test_city, bad_city],
        settings_path=settings_path,
        output_dir=output_dir,
    )

    assert len(results) == 2

    assert results[0].success is True
    assert results[1].success is False
    assert results[1].error is not None

    assert len(list(output_dir.glob("*.png"))) == 1
