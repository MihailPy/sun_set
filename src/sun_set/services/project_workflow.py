from dataclasses import dataclass

from sun_set.models.project_data import ProjectData
from sun_set.services.project_file_service import load_project, save_project


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


@dataclass(frozen=True)
class ProjectSaveSuccess:
    file_path: str


@dataclass(frozen=True)
class ProjectSaveError:
    message: str


ProjectSaveResult = ProjectSaveSuccess | ProjectSaveError


def execute_project_save(
    project: ProjectData,
    file_path: str,
) -> ProjectSaveResult:
    try:
        save_project(project, file_path)
        return ProjectSaveSuccess(file_path=file_path)

    except Exception as error:
        return ProjectSaveError(message=str(error))
