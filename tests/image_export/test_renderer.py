from pathlib import Path

import pytest
from PIL import Image
from pytest import fixture

from sun_set.image_export.errors import FontNotFoundError, TemplateNotFoundError
from sun_set.image_export.layout import TextBlock
from sun_set.image_export.renderer import load_font, render_image, render_image_to_pil
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
            first_column_offset_x=10,
            second_column_offset_x=100,
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


def test_render_image_no_template(settings_image, tmp_path: Path):
    """Тест создания изображения с нуля (без шаблона)."""
    output_path = tmp_path / "new_canvas.png"

    # Убеждаемся, что шаблона нет
    settings_image.image.template_path = None
    settings_image.image.width = 200
    settings_image.image.height = 100
    settings_image.image.background_color = "#FF0000"  # Красный

    render_image(
        settings=settings_image,
        text_blocks=[TextBlock(text="Hi", x=10, y=10)],
        output_path=output_path,
    )

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.size == (200, 100)
        # Проверяем цвет фона (первый пиксель)
        assert img.getpixel((0, 0)) == (255, 0, 0)


def test_render_image_with_template(settings_image, tmp_path: Path):
    """Тест создания изображения на основе существующего шаблона."""
    # 1. Создаем файл-шаблон (синий квадрат 50x50)
    template_path = tmp_path / "template.png"
    template_img = Image.new("RGB", (50, 50), "#0000FF")
    template_img.save(template_path)

    # 2. Настраиваем settings на этот шаблон
    settings_image.image.template_path = template_path
    output_path = tmp_path / "from_template.png"

    render_image(
        settings=settings_image,
        text_blocks=[TextBlock(text="On Template", x=5, y=5)],
        output_path=output_path,
    )

    assert output_path.exists()
    with Image.open(output_path) as img:
        # Размер должен взяться из шаблона (50x50), а не из настроек width/height
        assert img.size == (50, 50)
        # Проверяем, что фон остался синим
        assert img.getpixel((0, 0)) == (0, 0, 255)


def test_render_image_creates_nested_directories(settings_image, tmp_path: Path):
    """Проверка, что функция сама создает папки, если их нет."""
    output_path = tmp_path / "deep" / "nested" / "folder" / "result.png"

    render_image(settings_image, [], output_path)

    assert output_path.exists()


def test_render_image_with_missing_template_raises_error(
    settings_image, tmp_path: Path
):
    settings_image.image.template_path = tmp_path / "missing.png"

    with pytest.raises(TemplateNotFoundError):
        render_image(
            settings=settings_image,
            text_blocks=[],
            output_path=tmp_path / "out.png",
        )


def test_render_image_with_missing_font_raises_error(settings_image, tmp_path: Path):
    settings_image.text.font_path = str(tmp_path / "missing.ttf")

    with pytest.raises(FontNotFoundError):
        render_image(
            settings=settings_image,
            text_blocks=[],
            output_path=tmp_path / "out.png",
        )


def test_load_default_font(settings_image):
    settings_image.text.font_path = None

    font = load_font(settings_image.text)

    assert font is not None


def test_render_image_to_pil_returns_image(settings_image):
    image = render_image_to_pil(
        settings=settings_image,
        text_blocks=[
            TextBlock(text="17:10", x=50, y=50),
        ],
    )

    assert image.size == (
        settings_image.image.width,
        settings_image.image.height,
    )
