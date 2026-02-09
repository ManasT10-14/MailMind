from src.schema.email_object import EmailObject
from src.schema.summarizer_schema import SummarizerSchema
from typing import TypedDict,Any
from operator import or_


class SummarizerState(TypedDict):
    email: EmailObject
    summary: SummarizerSchema
    cache: Any
    llm: Any
    provider: Any