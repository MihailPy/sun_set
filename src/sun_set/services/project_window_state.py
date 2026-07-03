from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectWindowState:
    file_path: str | None = None

    def get_file_name(self) -> str | None:
        if self.file_path is None:
            return None

        return Path(self.file_path).name

    def get_status_file_text(self) -> str:
        file_name = self.get_file_name()

        if file_name is None:
            return "Файл не открыт"

        return f"Файл: {file_name}"
