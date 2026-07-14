import sys
from pathlib import Path


def get_resource_base_path() -> Path:
    bundled_path = getattr(sys, "_MEIPASS", None)

    if bundled_path is not None:
        return Path(bundled_path)

    return Path(__file__).resolve().parents[2]


def get_user_guide_path() -> Path:
    return get_resource_base_path() / "docs" / "user_guide.md"
