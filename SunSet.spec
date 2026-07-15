import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


project_root = Path(SPECPATH)

hidden_imports = collect_submodules("astral")

icon_path = None

if sys.platform == "darwin":
    icon_path = str(
        project_root / "assets" / "icons" / "sunset.icns"
    )
elif sys.platform == "win32":
    icon_path = str(
        project_root / "assets" / "icons" / "sunset.ico"
    )

datas = [
    (
        str(project_root / "docs" / "user_guide.md"),
        "docs",
    ),
    (
        str(project_root / "examples" / "image_export"),
        "examples/image_export",
    ),
]

analysis = Analysis(
    ["src/sun_set/main.py"],
    pathex=[str(project_root / "src")],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(analysis.pure)

exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="SunSet",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=icon_path,
)

collect = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SunSet",
)

if sys.platform == "darwin":
    app = BUNDLE(
        collect,
        name="SunSet.app",
        icon=icon_path,
        bundle_identifier="com.mihailpy.sunset",
    )
