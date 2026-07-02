from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from sun_set.image_export.errors import ImageExportError, get_user_friendly_error
from sun_set.image_export.service import (
    ExportResult,
    build_city_image_preview,
    build_export_summary_message,
    export_cities_images,
    save_export_report,
)
from sun_set.image_export.settings import load_export_settings
from sun_set.models.city import City
from sun_set.services.dialog_service import (
    ask_open_folder_after_export,
    open_directory,
)


@dataclass(frozen=True)
class ImageExportRequest:
    cities: list[City]
    settings_path: Path
    output_dir: Path


@dataclass(frozen=True)
class ImagePreviewRequest:
    city: City
    settings_path: Path


@dataclass(frozen=True)
class ImageExportSuccessResult:
    results: list[ExportResult]


@dataclass(frozen=True)
class ImageExportErrorResult:
    error_message: str


ImageExportExecutionResult = ImageExportSuccessResult | ImageExportErrorResult


@dataclass(frozen=True)
class ImagePreviewSuccessResult:
    image: Image.Image


@dataclass(frozen=True)
class ImagePreviewErrorResult:
    error_message: str


ImagePreviewExecutionResult = ImagePreviewSuccessResult | ImagePreviewErrorResult


@dataclass(frozen=True)
class ImageExportSettingsLoadSuccess:
    settings: object


@dataclass(frozen=True)
class ImageExportSettingsLoadError:
    message: str


ImageExportSettingsLoadResult = (
    ImageExportSettingsLoadSuccess | ImageExportSettingsLoadError
)


def export_selected_city_images(
    request: ImageExportRequest,
) -> list[ExportResult]:
    results = export_cities_images(
        cities=request.cities,
        settings_path=request.settings_path,
        output_dir=request.output_dir,
    )

    save_export_report(results, request.output_dir)

    return results


def build_selected_city_preview_image(
    request: ImagePreviewRequest,
) -> Image.Image:
    return build_city_image_preview(
        city=request.city,
        settings_path=request.settings_path,
    )


def build_image_export_result_message(results: list[ExportResult]) -> str:
    return build_export_summary_message(results)


def show_image_export_result_dialog(
    parent,
    results: list[ExportResult],
    output_dir: Path,
) -> None:
    message = build_image_export_result_message(results)

    if ask_open_folder_after_export(parent, message):
        open_directory(output_dir)


def build_image_export_request(
    cities: list[City],
    settings_path: Path,
    output_dir: Path,
) -> ImageExportRequest:
    return ImageExportRequest(
        cities=cities,
        settings_path=settings_path,
        output_dir=output_dir,
    )


def build_image_preview_request(
    city: City,
    settings_path: Path,
) -> ImagePreviewRequest:
    return ImagePreviewRequest(
        city=city,
        settings_path=settings_path,
    )


def get_image_export_error_message(error: Exception) -> str:
    return get_user_friendly_error(error)


def execute_image_export(
    request: ImageExportRequest,
) -> ImageExportExecutionResult:
    try:
        results = export_selected_city_images(request)
        return ImageExportSuccessResult(results=results)

    except Exception as error:
        return ImageExportErrorResult(
            error_message=get_image_export_error_message(error)
        )


def execute_image_preview(
    request: ImagePreviewRequest,
) -> ImagePreviewExecutionResult:
    try:
        image = build_selected_city_preview_image(request)
        return ImagePreviewSuccessResult(image=image)

    except Exception as error:
        return ImagePreviewErrorResult(
            error_message=get_image_export_error_message(error)
        )


def execute_image_export_settings_load(
    settings_path: Path,
) -> ImageExportSettingsLoadResult:
    try:
        settings = load_export_settings(settings_path)
        return ImageExportSettingsLoadSuccess(settings=settings)

    except ImageExportError as error:
        return ImageExportSettingsLoadError(
            message=get_image_export_error_message(error)
        )

    except Exception as error:
        return ImageExportSettingsLoadError(message=str(error))
