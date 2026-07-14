from sun_set.resources import (
    get_resource_base_path,
    get_user_guide_path,
)


def test_get_resource_base_path_for_source_run():
    path = get_resource_base_path()

    assert path.is_absolute()


def test_get_user_guide_path_for_source_run():
    path = get_user_guide_path()

    assert path.name == "user_guide.md"
    assert path.parent.name == "docs"


def test_get_resource_base_path_for_bundled_run(monkeypatch, tmp_path):
    monkeypatch.setattr(
        "sun_set.resources.sys._MEIPASS",
        str(tmp_path),
        raising=False,
    )

    assert get_resource_base_path() == tmp_path
