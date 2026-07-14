from unittest.mock import patch

from sun_set.app_info import get_app_version


@patch("sun_set.app_info.version")
def test_get_app_version(mock_version):
    mock_version.return_value = "1.2.3"

    assert get_app_version() == "1.2.3"


@patch("sun_set.app_info.version")
def test_get_app_version_dev(mock_version):
    from importlib.metadata import PackageNotFoundError

    mock_version.side_effect = PackageNotFoundError

    assert get_app_version() == "dev"
