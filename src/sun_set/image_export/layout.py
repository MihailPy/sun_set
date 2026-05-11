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

    min_wd = min(all_weekdays)

    for month in city.sunset_data.months or []:
        rows_data = []
        index = 0

        while index < len(month.days):
            day = month.days[index]

            next_day = month.days[index + 1] if index + 1 < len(month.days) else None

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
                index += 2
            else:
                is_first_col = day.weekday == min_wd

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
                index += 1

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
    month: SunsetExportMonth,
    layout: LayoutSettings,
) -> list[TextBlock]:
    month_block = layout.month_blocks[month.month]

    text_blocks: list[TextBlock] = []

    for index, row in enumerate(month.rows):
        y = month_block.y + index * layout.row_height

        if row.first_day_sunset is not None:
            text_blocks.append(
                TextBlock(
                    text=f"{row.first_day_sunset.day} — {row.first_day_sunset.time}",
                    x=month_block.x + layout.meeting_offset_x,
                    y=y,
                )
            )

        if row.second_day_sunset is not None:
            text_blocks.append(
                TextBlock(
                    text=f"{row.second_day_sunset.day} — {row.second_day_sunset.time}",
                    x=month_block.x + layout.sunset_offset_x,
                    y=y,
                )
            )

    return text_blocks
