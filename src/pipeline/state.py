from typing import List,Any,Dict,TypedDict
from src.schema.email_object import EmailObject
from src.schema.router_schema import RouterSchema
from src.schema.summarizer_schema import SummarizerSchema
from src.schema.draft_reply_schema import DraftReplySchema
from src.schema.calendar_event_schema import CalendarEventSchema
class ParentState(TypedDict):
    emails: List[EmailObject]

    actions: Dict[str, RouterSchema]
    current_index: int
    start_date: str
    end_date: str
    # worker outputs
    summaries: Dict[str, SummarizerSchema]
    drafts: Dict[str, DraftReplySchema]
    calendar_events: Dict[str, CalendarEventSchema]
    
    # infra
    cache: Any
    llm: Any
    provider: Any
    embedding_model: Any
    defer: bool
    defer_email: EmailObject
    
    defer_context: List[str]