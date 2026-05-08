from sun_set.image_export.layout import build_text_blocks_for_month
from sun_set.image_export.settings import LayoutSettings, MonthBlockSettings


def test_build_text_blocks_for_month():
    layout = LayoutSettings(
        row_height=30,
        meeting_offset_x=10,
        sunset_offset_x=100,
        month_blocks={
            1: MonthBlockSettings(x=40, y=200),
        },
    )

    blocks = build_text_blocks_for_month(
        month=1,
        rows=[
            ("17:10", "17:45"),
            ("17:20", "17:55"),
        ],
        layout=layout,
    )

    assert len(blocks) == 4

    assert blocks[0].text == "17:10"
    assert blocks[0].x == 50
    assert blocks[0].y == 200

    assert blocks[1].text == "17:45"
    assert blocks[1].x == 140
    assert blocks[1].y == 200

    assert blocks[2].text == "17:20"
    assert blocks[2].x == 50
    assert blocks[2].y == 230

    assert blocks[3].text == "17:55"
    assert blocks[3].x == 140
    assert blocks[3].y == 230
