from src.schema.email_object import EmailObject
from src.schema.router_schema import RouterSchema
from typing import List,TypedDict,Dict,Literal,Any,Annotated
from operator import or_

class RouterState(TypedDict):
    emails: List[EmailObject]
    batches: Dict[str,List[EmailObject]]
    actions: Annotated[Dict[str,RouterSchema],or_]
    cache: Any
    llm: Any
    provider: Any