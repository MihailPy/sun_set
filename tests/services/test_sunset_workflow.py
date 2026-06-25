from unittest.mock import Mock, patch

from sun_set.services.sunset_workflow import (
    SingleCitySunsetUpdateRequest,
    SunsetSettings,
    SunsetUpdateRequest,
    build_single_city_sunset_update_request,
    build_sunset_update_request,
    execute_single_city_sunset_update,
    execute_sunset_update,
)


def test_build_sunset_update_request():
    settings = SunsetSettings(
        year=2027,
        weekday1=4,
        weekday2=5,
    )

    request = build_sunset_update_request(
        cities=[],
        settings=settings,
    )

    assert isinstance(request, SunsetUpdateRequest)
    assert request.cities == []
    assert request.settings == settings


@patch("sun_set.services.sunset_workflow.update_cities_sunset")
def test_execute_sunset_update(mock_update_cities_sunset):
    settings = SunsetSettings(
        year=2027,
        weekday1=4,
        weekday2=5,
    )

    request = SunsetUpdateRequest(
        cities=[],
        settings=settings,
    )

    execute_sunset_update(request)

    mock_update_cities_sunset.assert_called_once_with(
        [],
        2027,
        4,
        5,
    )


def test_sunset_settings():
    settings = SunsetSettings(
        year=2027,
        weekday1=4,
        weekday2=5,
    )

    assert settings.year == 2027
    assert settings.weekday1 == 4
    assert settings.weekday2 == 5


def test_build_single_city_sunset_update_request():
    city = Mock()
    settings = SunsetSettings(
        year=2027,
        weekday1=4,
        weekday2=5,
    )

    request = build_single_city_sunset_update_request(
        city=city,
        settings=settings,
    )

    assert isinstance(request, SingleCitySunsetUpdateRequest)
    assert request.city == city
    assert request.settings == settings


@patch("sun_set.services.sunset_workflow.update_city_sunset")
def test_execute_single_city_sunset_update(mock_update_city_sunset):
    city = Mock()
    settings = SunsetSettings(
        year=2027,
        weekday1=4,
        weekday2=5,
    )
    request = SingleCitySunsetUpdateRequest(
        city=city,
        settings=settings,
    )

    execute_single_city_sunset_update(request)

    mock_update_city_sunset.assert_called_once_with(
        city,
        2027,
        4,
        5,
    )
