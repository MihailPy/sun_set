import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules


project_root = Path(SPECPATH)

hidden_imports = collect_submodules("astral")

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
        icon=None,
        bundle_identifier="com.mihailpy.sunset",
    )
