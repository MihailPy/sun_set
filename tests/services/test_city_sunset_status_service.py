from sun_set.models.sunset import Source
from sun_set.models.table_model import (
    CHECK_COLUMN,
    CITY_NAME_COLUMN,
    ELEVATION_COLUMN,
    LAT_COLUMN,
    LON_COLUMN,
    REGION_COLUMN,
    STATUS_COLUMN,
    SUNSET_DATA_COLUMN,
    TIMEZONE_COLUMN,
    is_editable_city_column,
)
from sun_set.services.city_sunset_status_service import (
    build_city_sunset_status_text,
    can_open_city_sunset_data,
)


def test_build_city_sunset_status_text_changed_city(sample_city):
    sample_city.sunset_data.hash_before_edit = "old-hash"

    assert build_city_sunset_status_text(sample_city) == "Требует обновления"


def test_build_city_sunset_status_text_calculated(sample_city):
    sample_city.sunset_data.hash_before_edit = sample_city.get_stable_hash()
    sample_city.sunset_data.source = Source.CALCULATED

    assert build_city_sunset_status_text(sample_city) == "Актуально"


def test_build_city_sunset_status_text_edited(sample_city):
    sample_city.sunset_data.hash_before_edit = sample_city.get_stable_hash()
    sample_city.sunset_data.source = Source.EDITED

    assert build_city_sunset_status_text(sample_city) == "Изменено вручную"


def test_build_city_sunset_status_text_error_polar(sample_city):
    sample_city.sunset_data.hash_before_edit = sample_city.get_stable_hash()
    sample_city.sunset_data.source = Source.ERROR_POLAR

    assert build_city_sunset_status_text(sample_city) == "Ошибка расчёта"


def test_can_open_city_sunset_data_when_months_exist(sample_city):
    sample_city.sunset_data.months = {"1": []}

    assert can_open_city_sunset_data(sample_city)


def test_can_open_city_sunset_data_when_months_empty(sample_city):
    sample_city.sunset_data.months = {}

    assert not can_open_city_sunset_data(sample_city)


def test_is_editable_city_column():
    assert is_editable_city_column(CITY_NAME_COLUMN)
    assert is_editable_city_column(REGION_COLUMN)
    assert is_editable_city_column(LAT_COLUMN)
    assert is_editable_city_column(LON_COLUMN)
    assert is_editable_city_column(TIMEZONE_COLUMN)
    assert is_editable_city_column(ELEVATION_COLUMN)

    assert not is_editable_city_column(CHECK_COLUMN)
    assert not is_editable_city_column(STATUS_COLUMN)
    assert not is_editable_city_column(SUNSET_DATA_COLUMN)
