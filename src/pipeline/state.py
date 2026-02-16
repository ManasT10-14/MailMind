from typing import List,Any,Dict,TypedDict,Annotated
from src.schema.email_object import EmailObject
from src.schema.router_schema import RouterSchema
from src.schema.summarizer_schema import SummarizerSchema
from src.schema.draft_reply_schema import DraftReplySchema
from src.schema.calendar_event_schema import CalendarEventSchema
from operator import or_

class ParentState(TypedDict):
    emails: List[EmailObject]

    actions: Dict[str, RouterSchema]
    current_index: int
    start_date: str
    end_date: str
    # worker outputs
    summaries: Annotated[Dict[str, SummarizerSchema],or_]
    drafts: Annotated[Dict[str, DraftReplySchema],or_]
    calendar_events: Annotated[Dict[str, CalendarEventSchema],or_]
    
    # infra
    cache: Any
    llm: Any
    provider: Any
    embedding_model: Any
    defer: bool
    defer_email: EmailObject
    
    defer_context: List[str]