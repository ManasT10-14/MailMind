from typing import Dict,Any,List
from src.schema.email_object import EmailObject
from src.schema.router_schema import RouterSchema


def build_initial_state(*,cache:Any,llm:Any,provider:Any,embedding_model:Any,email:EmailObject,action:RouterSchema) -> Dict[str,Any]:

    return {
        "cache": cache,
        "llm": llm,
        "provider": provider,
        "embedding_model":embedding_model,
        "email":email,
        "email_action_details":action,
    }

