from dataclasses import dataclass

from sun_set.models.project_data import ProjectData
from sun_set.services.project_file_service import load_project


@dataclass(frozen=True)
class ProjectLoadSuccess:
    project: ProjectData


@dataclass(frozen=True)
class ProjectLoadError:
    message: str


ProjectLoadResult = ProjectLoadSuccess | ProjectLoadError


def execute_project_load(file_path: str) -> ProjectLoadResult:
    project, error = load_project(file_path)

    if error is not None:
        return ProjectLoadError(message=error)

    if project is None:
        return ProjectLoadError(message="Не удалось загрузить проект.")

    return ProjectLoadSuccess(project=project)
