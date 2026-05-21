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
    image = render_image_to_pil(settings, text_blocks)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)


def render_image_to_pil(
    settings: ExportImageSettings,
    text_blocks: list[TextBlock],
) -> Image.Image:
    image = create_base_image(settings)
    font = load_font(settings.text)

    draw = ImageDraw.Draw(image)

    for text_block in text_blocks:
        draw.text(
            (text_block.x, text_block.y),
            text_block.text,
            fill=settings.text.color,
            font=font,
        )

    return image


def create_base_image(settings: ExportImageSettings) -> Image.Image:
    if settings.image.template_path is None:
        return Image.new(
            "RGB",
            (settings.image.width, settings.image.height),
            settings.image.background_color,
        )

    template_path = Path(settings.image.template_path)

    if not template_path.exists():
        raise TemplateNotFoundError(f"Template file not found: {template_path}")

    with Image.open(template_path) as template:
        return template.convert("RGB")


def load_font(
    text_settings: TextSettings,
) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if text_settings.font_path is None:
        return ImageFont.load_default(text_settings.font_size)

    font_path = Path(text_settings.font_path)

    if not font_path.exists():
        raise FontNotFoundError(f"Font file not found: {font_path}")

    return ImageFont.truetype(str(font_path), text_settings.font_size)
