from datetime import date, datetime, timedelta
from typing import Optional

from .date_range import date_range


def format_dates(
    date: Optional[str], range: Optional[tuple[str, str]], delta: int = 1
) -> list[date]:
    yesterday = (datetime.today() - timedelta(days=delta)).strftime("%d/%m/%Y")
    dates = (yesterday, None)
    if range:
        dates = range
    elif date:
        dates = (date, None)

    dates = date_range(*dates)

    return dates
