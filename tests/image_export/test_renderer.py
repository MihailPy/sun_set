from pathlib import Path

import pytest
from PIL import Image

from sun_set.image_export.errors import FontNotFoundError, TemplateNotFoundError
from sun_set.image_export.layout import TextBlock
from sun_set.image_export.renderer import load_font, render_image, render_image_to_pil


def test_render_image_creates_file(export_settings, text_blocks, tmp_path: Path):
    output_path = tmp_path / "test.png"

    render_image(
        settings=export_settings,
        text_blocks=text_blocks,
        output_path=output_path,
    )

    assert output_path.exists()

    image = Image.open(output_path)
    assert image.size == (400, 300)


def test_render_image_no_template(export_settings, text_blocks, tmp_path: Path):
    """Тест создания изображения с нуля (без шаблона)."""
    output_path = tmp_path / "new_canvas.png"

    # Убеждаемся, что шаблона нет
    export_settings.image.template_path = None
    export_settings.image.width = 200
    export_settings.image.height = 100
    export_settings.image.background_color = "#FF0000"  # Красный

    render_image(
        settings=export_settings,
        text_blocks=text_blocks,
        output_path=output_path,
    )

    assert output_path.exists()
    with Image.open(output_path) as img:
        assert img.size == (200, 100)
        # Проверяем цвет фона (первый пиксель)
        assert img.getpixel((0, 0)) == (255, 0, 0)


def test_render_image_with_template(export_settings, text_blocks, tmp_path: Path):
    """Тест создания изображения на основе существующего шаблона."""
    # 1. Создаем файл-шаблон (синий квадрат 50x50)
    template_path = tmp_path / "template.png"
    template_img = Image.new("RGB", (50, 50), "#0000FF")
    template_img.save(template_path)

    # 2. Настраиваем settings на этот шаблон
    export_settings.image.template_path = template_path
    output_path = tmp_path / "from_template.png"

    render_image(
        settings=export_settings,
        text_blocks=text_blocks,
        output_path=output_path,
    )

    assert output_path.exists()
    with Image.open(output_path) as img:
        # Размер должен взяться из шаблона (50x50), а не из настроек width/height
        assert img.size == (50, 50)
        # Проверяем, что фон остался синим
        assert img.getpixel((0, 0)) == (0, 0, 255)


def test_render_image_creates_nested_directories(export_settings, tmp_path: Path):
    """Проверка, что функция сама создает папки, если их нет."""
    output_path = tmp_path / "deep" / "nested" / "folder" / "result.png"

    render_image(export_settings, [], output_path)

    assert output_path.exists()


def test_render_image_with_missing_template_raises_error(
    export_settings, tmp_path: Path
):
    export_settings.image.template_path = tmp_path / "missing.png"

    with pytest.raises(TemplateNotFoundError):
        render_image(
            settings=export_settings,
            text_blocks=[],
            output_path=tmp_path / "out.png",
        )


def test_render_image_with_missing_font_raises_error(export_settings, tmp_path: Path):
    export_settings.text.font_path = str(tmp_path / "missing.ttf")

    with pytest.raises(FontNotFoundError):
        render_image(
            settings=export_settings,
            text_blocks=[],
            output_path=tmp_path / "out.png",
        )


def test_load_default_font(export_settings):
    export_settings.text.font_path = None

    font = load_font(export_settings.text)

    assert font is not None


def test_render_image_to_pil_returns_image(export_settings):
    image = render_image_to_pil(
        settings=export_settings,
        text_blocks=[
            TextBlock(text="17:10", x=50, y=50),
        ],
    )

    assert image.size == (
        export_settings.image.width,
        export_settings.image.height,
    )
