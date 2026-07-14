from pathlib import Path


def get_project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def get_user_guide_path() -> Path:
    return get_project_root() / "docs" / "user_guide.md"
