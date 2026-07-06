from sun_set.models.city import City
from sun_set.models.sunset import Source


def build_city_sunset_status_text(city: City) -> str:
    if city.get_stable_hash() != city.sunset_data.hash_before_edit:
        return "Требует обновления"

    if city.sunset_data.source == Source.CALCULATED:
        return "Актуально"

    if city.sunset_data.source == Source.EDITED:
        return "Изменено вручную"

    if city.sunset_data.source == Source.ERROR_POLAR:
        return "Ошибка расчёта"

    return "Нет данных"


def can_open_city_sunset_data(city: City) -> bool:
    return bool(city.sunset_data.months)
