from importlib.metadata import PackageNotFoundError, version


def get_app_version() -> str:
    try:
        return version("sun-set")
    except PackageNotFoundError:
        return "dev"
