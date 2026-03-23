import calendar
import datetime
from zoneinfo import ZoneInfo

from astral import Observer
from astral.sun import sunset

from sun_set.models.city import City
from sun_set.models.sunset import MonthData, Source, SunsetEntry, YearData


def get_city_sunset(city: City, year: int, weekday1: int, weekday2: int) -> YearData:
    obs = Observer(city.lat, city.lon, city.elevation)
    # ModuleNotFoundError: No module named 'tzdata'
    city_tz = ZoneInfo(city.timezone)
    weekdays_to_check = {weekday1, weekday2}
    allowed_weekdays = {0, 1, 2, 3, 4, 5, 6}
    has_invalid_weekdays = not weekdays_to_check <= allowed_weekdays
    if has_invalid_weekdays:
        raise ValueError("Присутствуют недопустимые числа в weekday1 или  weekday2")

    sunset_city_year = []

    for month in range(1, 13):
        sunset_city_month = []
        _, last_day = calendar.monthrange(year, month)

        for day in range(1, last_day + 1):
            current_date = datetime.date(year, month, day)

            if current_date.weekday() in weekdays_to_check:
                try:
                    res = sunset(obs, date=current_date, tzinfo=city_tz)
                    time_str = res.strftime("%H:%M")
                    res_day = SunsetEntry(
                        day, current_date.weekday(), time_str, Source.CALCULATED
                    )
                except ValueError:
                    res_day = SunsetEntry(
                        day, current_date.weekday(), "00:00", Source.ERROR_POLAR
                    )

                sunset_city_month.append(res_day)

        if sunset_city_month:
            sunset_city_year.append(MonthData(month, sunset_city_month))

    return YearData(year, Source.CALCULATED, city.get_stable_hash(), sunset_city_year)
