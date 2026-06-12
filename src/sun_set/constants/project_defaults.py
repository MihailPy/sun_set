from datetime import datetime

DEFAULT_WEEKDAY_1 = 4
DEFAULT_WEEKDAY_2 = 5


def get_default_project_year() -> int:
    return datetime.now().year + 1
