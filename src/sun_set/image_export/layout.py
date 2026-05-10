# превращает данные города в текстовые блоки


from dataclasses import dataclass

from sun_set.image_export.settings import LayoutSettings
from sun_set.models.city import City


@dataclass
class SunsetExportDay:
    day: str
    time: str


@dataclass
class SunsetExportRow:
    first_day_sunset: SunsetExportDay | None
    second_day_sunset: SunsetExportDay | None


@dataclass
class SunsetExportMonth:
    month: int
    rows: list[SunsetExportRow]


@dataclass
class SunsetExportData:
    city_name: str
    year: int
    months: list[SunsetExportMonth]


def build_export_data_from_city(city: City) -> SunsetExportData:
    data_months = []

    all_weekdays = {d.weekday for m in (city.sunset_data.months or []) for d in m.days}
    if not all_weekdays:
        return SunsetExportData(
            city_name=city.name, year=city.sunset_data.year, months=[]
        )

    first_wd = min(all_weekdays)

    for month in city.sunset_data.months or []:
        rows_data = []
        days_iter = iter(month.days)

        for day in days_iter:
            next_day = next(days_iter, None)

            if next_day and next_day.day == day.day + 1:
                rows_data.append(
                    SunsetExportRow(
                        first_day_sunset=SunsetExportDay(
                            day=str(day.day), time=day.time
                        ),
                        second_day_sunset=SunsetExportDay(
                            day=str(next_day.day), time=next_day.time
                        ),
                    )
                )
            else:
                is_first_col = day.weekday == first_wd

                rows_data.append(
                    SunsetExportRow(
                        first_day_sunset=SunsetExportDay(
                            day=str(day.day), time=day.time
                        )
                        if is_first_col
                        else None,
                        second_day_sunset=SunsetExportDay(
                            day=str(day.day), time=day.time
                        )
                        if not is_first_col
                        else None,
                    )
                )

        data_months.append(SunsetExportMonth(month=month.month, rows=rows_data))

    return SunsetExportData(
        city_name=city.name, year=city.sunset_data.year, months=data_months
    )


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
