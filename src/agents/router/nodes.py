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
from src.agents.router.state import RouterState

def batch_emails(state: RouterState):
    print(state)
    emails = state["emails"]
    print(emails)
    batch:Dict[str,List[EmailObject]] = batch_by_sender_and_time(emails=emails)
    return {"batches":batch}
def fan_out_batches(state: RouterState):
    batch = state["batches"]
    
    return [
        
        Send("process_batch",{"batch_emails":emails,"cache":state["cache"],"llm":state["llm"],"provider":state["provider"],"defer":state["defer"],"defer_context":state["defer_context"]}) for _,emails in batch.items()
        
    ]
    
def process_batch(state: RouterState):
    emails:List[EmailObject] = state["batch_emails"]
    email_context = []
    if state["defer"]:
        email_context = state["defer_context"]
    
    actions = {}
    for email in emails:
        email_prompt  = build_router_agent_prompt(email=email,prev_summary=email_context)
        result:RouterSchema = call_llm_cached(cache=state["cache"],llm=state["llm"],provider=state["provider"],model_name=MODEL_NAME,system_prompt=SYSTEM_PROMPT_ROUTER_AGENT,user_prompt=email_prompt,output_schema=RouterSchema,prompt_version=PROMPT_VERSION_ROUTER_AGENT,agent_name="RouterAgent",cache_enabled=True)
        email_context = result.rolling_summary
        actions[email.message_id] = result
    
    return {"actions":actions}
    