import shutil
import subprocess
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]

    for directory_name in ("build", "dist"):
        directory = project_root / directory_name
        if directory.exists():
            shutil.rmtree(directory)

    subprocess.run(
        [
            "pyinstaller",
            "--clean",
            "--noconfirm",
            str(project_root / "SunSet.spec"),
        ],
        cwd=project_root,
        check=True,
    )


if __name__ == "__main__":
    main()
