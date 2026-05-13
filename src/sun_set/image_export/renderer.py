# рисует текст на изображении
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from sun_set.image_export.errors import FontNotFoundError, TemplateNotFoundError
from sun_set.image_export.layout import TextBlock
from sun_set.image_export.settings import ExportImageSettings, TextSettings


def render_image(
    settings: ExportImageSettings,
    text_blocks: list[TextBlock],
    output_path: Path,
) -> None:
    if settings.image.template_path is None:
        image = Image.new(
            "RGB",
            (settings.image.width, settings.image.height),
            settings.image.background_color,
        )
    else:
        template_path = Path(settings.image.template_path)
        if not template_path.exists():
            raise TemplateNotFoundError(f"Template file not found: {template_path}")
        with Image.open(template_path) as template:
            image = template.convert("RGB")

    font = load_font(settings.text)

    draw = ImageDraw.Draw(image)

    for text_block in text_blocks:
        draw.text(
            (text_block.x, text_block.y),
            text_block.text,
            fill=settings.text.color,
            font=font,
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def load_font(
    text_settings: TextSettings,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if text_settings.font_path is None:
        return ImageFont.load_default(text_settings.font_size)

    font_path = Path(text_settings.font_path)

    if not font_path.exists():
        raise FontNotFoundError(f"Font file not found: {font_path}")

    return ImageFont.truetype(str(font_path), text_settings.font_size)
