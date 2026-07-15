from pathlib import Path


def test_pyinstaller_spec_includes_required_resources():
    project_root = Path(__file__).resolve().parents[2]
    spec_text = (project_root / "SunSet.spec").read_text(encoding="utf-8")

    assert '"docs"' in spec_text
    assert '"user_guide.md"' in spec_text

    assert '"examples"' in spec_text
    assert '"image_export"' in spec_text

    assert '"src/sun_set/main.py"' in spec_text


def test_pyinstaller_spec_configures_platform_icons():
    project_root = Path(__file__).resolve().parents[2]
    spec_text = (project_root / "SunSet.spec").read_text(encoding="utf-8")

    assert '"sunset.icns"' in spec_text
    assert '"sunset.ico"' in spec_text
    assert "icon=icon_path" in spec_text
