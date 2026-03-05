from typing import List,Any,Dict,TypedDict,Annotated,Optional,Literal
from src.schema.email_object import EmailObject
from src.schema.router_schema import RouterSchema
from src.schema.summarizer_schema import SummarizerSchema
from src.schema.draft_reply_schema import DraftReplySchema
from src.schema.calendar_event_schema import CalendarEventSchema
from operator import or_
from pydantic import BaseModel

class UserDecision(BaseModel):
    message_id: str
    approved: bool
    type: Literal["draft", "calendar_event"]
    edited_draft: Optional[DraftReplySchema]
    edited_calendar_event: Optional[CalendarEventSchema]

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
    
    #HITL
    hitl_queue: List[str]  # message_ids requiring approval
    hitl_index: int
    approved_actions: Dict[str, bool]
    hitl_payload: Dict[str,Any]
    status: str
    user_decision: Optional[UserDecision]
    
    
    trace: List[str]