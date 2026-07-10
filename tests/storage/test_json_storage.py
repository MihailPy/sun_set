import pytest

from sun_set.storage.json_storage import read_json, write_json


def test_write_and_read_json(tmp_path):
    path = tmp_path / "data.json"
    data = {
        "name": "Test",
        "items": [1, 2, 3],
    }

    write_json(path, data)

    assert path.exists()
    assert read_json(path) == data


def test_write_json_creates_parent_directory(tmp_path):
    path = tmp_path / "nested" / "data.json"

    write_json(path, {"ok": True})

    assert path.exists()
    assert read_json(path) == {"ok": True}


def test_write_json_to_directory(tmp_path):
    with pytest.raises(IsADirectoryError):
        write_json(tmp_path, {"test": True})
