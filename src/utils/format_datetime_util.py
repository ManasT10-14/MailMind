from datetime import datetime

def format_datetime(dt: datetime) -> str:
    """
    Format datetime as: day/month/year time: hr:min:sec:ms
    Example: 07/02/2026 time: 14:35:12:123
    """
    return dt.strftime("Date: %d/%m/%Y Time: %H:%M:%S:%f")[:-3]