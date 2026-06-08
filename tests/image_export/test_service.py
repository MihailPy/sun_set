from pathlib import Path

from sun_set.image_export.service import (
    ExportResult,
    build_export_report,
    build_export_summary_message,
    build_output_filename,
    export_cities_images,
    export_city_image,
    save_export_report,
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
    second_test_city,
    settings_path,
    tmp_path,
    monkeypatch,
):
    output_dir = tmp_path / "out"

    from sun_set.image_export import service

    real_build_export_data_from_city = service.build_export_data_from_city

    def fake_build_export_data_from_city(city):
        if city.name == "Bad City":
            raise RuntimeError("Test city error")

        return real_build_export_data_from_city(city)

    bad_city = second_test_city
    bad_city.name = "Bad City"

    monkeypatch.setattr(
        service,
        "build_export_data_from_city",
        fake_build_export_data_from_city,
    )

    results = export_cities_images(
        cities=[test_city, bad_city],
        settings_path=settings_path,
        output_dir=output_dir,
    )

    assert len(results) == 2

    assert results[0].success is True
    assert results[0].output_path is not None

    assert results[1].success is False
    assert results[1].output_path is None
    assert results[1].error is not None

    assert len(list(output_dir.glob("*.png"))) == 1


def test_build_export_report():
    results = [
        ExportResult(
            city_name="Amsterdam",
            output_path=Path("amsterdam.png"),
            success=True,
            error=None,
        ),
        ExportResult(
            city_name="Berlin",
            output_path=None,
            success=False,
            error="Ошибка экспорта",
        ),
    ]

    report = build_export_report(results)

    assert "Готово: 1" in report
    assert "Ошибки: 1" in report
    assert "OK: Amsterdam -> amsterdam.png" in report
    assert "ERROR: Berlin -> Ошибка экспорта" in report


def test_build_export_summary_message():
    results = [
        ExportResult(
            city_name="Amsterdam",
            output_path=Path("amsterdam.png"),
            success=True,
            error=None,
        ),
        ExportResult(
            city_name="Berlin",
            output_path=None,
            success=False,
            error="Ошибка экспорта",
        ),
    ]

    message = build_export_summary_message(results)

    assert "Готово: 1" in message
    assert "Ошибки: 1" in message
    assert "- Berlin: Ошибка экспорта" in message


def test_save_export_report(tmp_path):
    results = [
        ExportResult(
            city_name="Amsterdam",
            output_path=Path("amsterdam.png"),
            success=True,
            error=None,
        )
    ]

    report_path = save_export_report(results, tmp_path)

    assert report_path == tmp_path / "image_export_report.txt"
    assert report_path.exists()
    assert "Готово: 1" in report_path.read_text(encoding="utf-8")
