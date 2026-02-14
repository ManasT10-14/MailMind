from src.schema.email_object import EmailObject
from src.schema.router_schema import RouterSchema
from typing import List,TypedDict,Dict,Literal,Any,Annotated



class DeferState(TypedDict):
    email: EmailObject
    email_action_details: RouterSchema
    relevant_watches: List[Any]
    run_router: bool
    router_summary: List[str]
    cache: Any
    llm: Any
    provider: Any
    embedding_model: Any