import calendar
import datetime
from zoneinfo import ZoneInfo

from astral import Observer
from astral.sun import sunset

from sun_set.models.city import City
from sun_set.models.sunset import MonthData, Source, SunsetEntry


def get_city_sunset(city: City, year: int, weekday1: int, weekday2: int) -> list:
    print(f"{city=} {year=} {weekday1=} {weekday2=}")

    sunset_city_year = []
    sunset_city_month = []
    for month in range(1, 13):
        _, last_day = calendar.monthrange(year, month)

        for day in range(1, last_day + 1):
            data = datetime.date(year, month, day)
            weekday = data.weekday()

            if weekday == weekday1 or weekday == weekday2:
                # day_s = f"{day:02d}"

                obs = Observer(city.lat, city.lon, city.elevation)
                city_tz = ZoneInfo(city.timezone)
                res = sunset(obs, date=data, tzinfo=city_tz)
                hour = int(res.time().hour)
                minute = f"{int(res.time().minute):02d}"
                res_day = SunsetEntry(
                    day, weekday, f"{hour}:{minute}", Source.CALCULATED
                )
                sunset_city_month.append(res_day)
        res_month = MonthData(month, sunset_city_month)
        sunset_city_year.append(res_month)
        sunset_city_month = []

    return sunset_city_year
