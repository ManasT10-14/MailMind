from typing import Dict,Any,List
from src.schema.email_object import EmailObject
from src.schema.router_schema import RouterSchema

def build_initial_state(*,cache:Any,llm:Any,provider:Any,emails:List[EmailObject],actions:Dict[str,RouterSchema],defer:bool,defer_context: List[str] = None) -> Dict[str,Any]:

    return {
        "cache": cache,
        "llm": llm,
        "provider": provider,
        "emails":emails,
        "actions":actions,
        "defer":defer
    }

