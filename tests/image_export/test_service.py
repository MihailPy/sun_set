# from pathlib import Path

from sun_set.core.astronomy import get_city_sunset
from sun_set.image_export.service import export_city_image
from sun_set.models.city import City
from sun_set.models.sunset import Source, YearData


def test_export_city_image_creates_file(tmp_path):
    sunset_data = YearData(
        year=2024, source=Source.CALCULATED, hash_before_edit=None, months=None
    )

    city = City(
        name="Test City",
        region="Test Region",
        lat=55.7558,
        lon=37.6173,
        timezone="Europe/Moscow",
        elevation=170,
        sunset_data=sunset_data,
    )

    city.sunset_data = get_city_sunset(city, 2024, 0, 1)
    if city.sunset_data.months is not None:
        city.sunset_data.months = city.sunset_data.months[:3]

    settings_path = tmp_path / "settings.json"
    # settings_path = Path("tests/image_export/test_settings.py")
    output_path = tmp_path / "out.png"

    settings_path.write_text(
        """
        {
          "image": {
            "width": 400,
            "height": 300,
            "background_color": "#ffffff",
            "template_path": null
          },
          "text": {
            "font_path": null,
            "font_size": 20,
            "color": "#000000"
          },
          "layout": {
            "row_height": 30,
            "first_column_offset_x": 10,
            "second_column_offset_x": 120,
            "month_blocks": {
              "1": {"x": 40, "y": 50},
              "2": {"x": 80, "y": 50},
              "3": {"x": 40, "y": 100}
            }
          }
        }
        """,
        encoding="utf-8",
    )

    export_city_image(
        city=city,
        settings_path=settings_path,
        output_path=output_path,
    )

    assert output_path.exists()
