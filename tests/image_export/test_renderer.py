from pathlib import Path

from PIL import Image
from pytest import fixture

from sun_set.image_export.layout import TextBlock
from sun_set.image_export.renderer import render_image
from sun_set.image_export.settings import (
    ExportImageSettings,
    ImageSettings,
    LayoutSettings,
    TextSettings,
)


@fixture
def settings_image():
    return ExportImageSettings(
        image=ImageSettings(
            width=400,
            height=300,
            background_color="#ffffff",
            template_path=None,
        ),
        text=TextSettings(
            font_path=None,
            font_size=20,
            color="#000000",
        ),
        layout=LayoutSettings(
            row_height=30,
            meeting_offset_x=10,
            sunset_offset_x=100,
            month_blocks={},
        ),
    )


def test_render_image_creates_file(settings_image, tmp_path: Path):
    output_path = tmp_path / "test.png"

    render_image(
        settings=settings_image,
        text_blocks=[
            TextBlock(text="17:10", x=50, y=50),
            TextBlock(text="17:45", x=150, y=50),
        ],
        output_path=output_path,
    )

    assert output_path.exists()

    image = Image.open(output_path)
    assert image.size == (400, 300)
