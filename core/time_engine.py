from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import swisseph as swe


def calculate_julian_day(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int,
    timezone_name: str
) -> float:

    local_datetime = datetime(
        year,
        month,
        day,
        hour,
        minute,
        second,
        tzinfo=ZoneInfo(timezone_name)
    )

    utc_datetime = local_datetime.astimezone(timezone.utc)

    utc_hour = (
        utc_datetime.hour
        + utc_datetime.minute / 60.0
        + utc_datetime.second / 3600.0
    )

    julian_day = swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        utc_hour
    )

    return julian_day
