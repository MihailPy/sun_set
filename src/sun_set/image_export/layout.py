# превращает данные города в текстовые блоки


from dataclasses import dataclass

from sun_set.image_export.settings import LayoutSettings


@dataclass
class TextBlock:
    text: str
    x: int
    y: int


def build_text_blocks_for_month(
    month: int,
    rows: list[tuple[str, str]],
    layout: LayoutSettings,
) -> list[TextBlock]:
    month_blocks = layout.month_blocks[month]

    text_blocks: list[TextBlock] = []

    for index, (meeting_text, sunset_text) in enumerate(rows):
        y = month_blocks.y + index * layout.row_height

        text_blocks.append(
            TextBlock(
                text=meeting_text, x=month_blocks.x + layout.meeting_offset_x, y=y
            )
        )
        text_blocks.append(
            TextBlock(
                text=sunset_text,
                x=month_blocks.x + layout.sunset_offset_x,
                y=y,
            )
        )

    return text_blocks
