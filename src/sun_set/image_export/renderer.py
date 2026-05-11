# рисует текст на изображении
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from sun_set.image_export.layout import TextBlock
from sun_set.image_export.settings import ExportImageSettings


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
        with Image.open(settings.image.template_path) as template:
            image = template.convert("RGB")

    if settings.text.font_path is not None:
        font = ImageFont.truetype(
            settings.text.font_path,
            settings.text.font_size,
        )
    else:
        font = ImageFont.load_default(settings.text.font_size)

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
    image.show()
