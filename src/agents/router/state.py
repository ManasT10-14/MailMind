from src.prompts.router_agent_prompt import SYSTEM_PROMPT_ROUTER_AGENT,PROMPT_VERSION_ROUTER_AGENT,build_router_agent_prompt
from src.llm.service import call_llm_cached
from src.schema.email_object import EmailObject
from src.schema.router_schema import RouterSchema
from typing import List,TypedDict,Dict,Literal,Any,Annotated
from operator import or_
from langgraph.graph import StateGraph,START,END
from langgraph.types import Command,Send
from src.ingestion.batching import batch_by_sender_and_time
from src.config import MODEL_NAME

class RouterState(TypedDict):
    emails: List[EmailObject]
    batches: Dict[str,List[EmailObject]]
    actions: Annotated[Dict[str,RouterSchema],or_]
    cache: Any
    llm: Any
    provider: Any