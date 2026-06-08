from sun_set.models.project_data import ProjectData
from sun_set.storage.city_json_storage import (
    load_project_from_json,
    save_project_to_json,
)


def load_project(file_path: str) -> tuple[ProjectData | None, str | None]:
    return load_project_from_json(file_path)


def save_project(
    project: ProjectData,
    file_path: str,
) -> None:
    save_project_to_json(project, file_path)
