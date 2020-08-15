import datetime
from common.configs import datetime_format, TIMEZONE_UTC

DATETIME_FORMAT = datetime_format


def neotter_inner_to_datetime(datetime_str: str):
    """
    Translate Neotter inner datetime string to datetime object with timezone
    """
    return datetime.datetime.strptime(datetime_str, DATETIME_FORMAT) \
        .replace(tzinfo=TIMEZONE_UTC)


def datetime_to_neotter_inner(datetime_obj: datetime.datetime):
    return datetime_obj.astimezone(tz=TIMEZONE_UTC).strftime(DATETIME_FORMAT)


def day_after(days: int = 0):
    return datetime.datetime.now(tz=TIMEZONE_UTC) \
        + datetime.timedelta(days=days)
