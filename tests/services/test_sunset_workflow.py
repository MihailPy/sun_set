from unittest.mock import patch

from sun_set.services.sunset_workflow import (
    SunsetSettings,
    SunsetUpdateRequest,
    build_sunset_update_request,
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
    assert request.year == 2027
    assert request.weekday1 == 4
    assert request.weekday2 == 5


@patch("sun_set.services.sunset_workflow.update_cities_sunset")
def test_execute_sunset_update(mock_update_cities_sunset):
    request = SunsetUpdateRequest(
        cities=[],
        year=2027,
        weekday1=4,
        weekday2=5,
    )

    execute_sunset_update(request)

    mock_update_cities_sunset.assert_called_once_with(
        [],
        2027,
        4,
        5,
    )
