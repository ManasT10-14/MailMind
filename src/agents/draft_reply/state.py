from typing import TypedDict, Optional, List, Any
from src.schema.email_object import EmailObject
from src.schema.draft_reply_schema import DraftReplySchema


class DraftState(TypedDict):
    email: EmailObject
    context_summary: Optional[List[str]]
    cache: Any
    llm: Any
    provider: Any
    reply: DraftReplySchema
