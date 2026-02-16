from typing import Dict,Any,List
from src.schema.email_object import EmailObject

def build_initial_state(*,cache:Any,llm:Any,provider:Any,email:EmailObject) -> Dict[str,Any]:

    return {
        "cache": cache,
        "llm": llm,
        "provider": provider,
        "email":email,
    }

