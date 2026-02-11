from typing import TypedDict, Optional, List, Any
from src.schema.email_object import EmailObject
from src.schema.calendar_event_schema import CalendarEventSchema


class CalendarState(TypedDict):
    email : EmailObject
    cache: Any
    llm: Any
    provider: Any
    event_details: CalendarEventSchema