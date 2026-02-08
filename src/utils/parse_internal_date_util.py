from datetime import datetime, timezone

def parse_internal_date(internal_date: str) -> datetime:
    """
    Convert Gmail internalDate (ms since epoch) to UTC datetime.
    """
    return datetime.fromtimestamp(
        int(internal_date) / 1000,
        tz=timezone.utc
    )