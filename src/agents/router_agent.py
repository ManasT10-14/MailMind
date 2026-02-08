from src.prompts.router_agent_prompt import SYSTEM_PROMPT_ROUTER_AGENT,PROMPT_VERSION_ROUTER_AGENT,build_router_agent_prompt
from src.llm.service import call_llm_cached
from src.schema.email_object import EmailObject
from src.schema.router_schema import RouterSchema
from typing import List,TypedDict,Dict,Literal,Any
from langgraph.graph import StateGraph,START,END
from langgraph.types import Command,Send
from src.ingestion.batching import batch_by_sender_and_time
from src.config import MODEL_NAME

class RouterState(TypedDict):
    emails: List[EmailObject]
    batches: Dict[str,List[EmailObject]]
    actions: Dict[str,RouterSchema]
    cache: Any
    llm: Any
    provider: Any
    
def batch_emails(state: RouterState):
    emails = state["emails"]
    batch:Dict[str,List[EmailObject]] = batch_by_sender_and_time(emails=emails)
    return {"batches":batch}
def fan_out_batches(state: RouterState):
    batch = state["batches"]
    
    return [
        
        Send("process_batch",{"batch_emails":emails}) for _,emails in batch.items()
        
    ]
    
def process_batch(state: RouterState):
    emails:List[EmailObject] = state["batch_emails"]
    email_context = []
    for email in emails:
        email_prompt  = build_router_agent_prompt(email=email,prev_summary=email_context)
        result:RouterSchema = call_llm_cached(cache=state["cache"],llm=state["llm"],provider=state["provider"],model_name=MODEL_NAME,system_prompt=SYSTEM_PROMPT_ROUTER_AGENT,user_prompt=email_prompt,output_schema=RouterSchema,prompt_version=PROMPT_VERSION_ROUTER_AGENT,agent_name="RouterAgent",cache_enabled=True)
        email_context = result.rolling_summary
        return {"actions":{email.message_id:result}}
    
    
workflow = StateGraph(state_schema=RouterSchema)
workflow.add_node("batch_emails",batch_emails)
workflow.add_node("fan_out_batches",fan_out_batches)
workflow.add_node("process_batch",process_batch)

workflow.add_edge(START,"batch_emails")
workflow.add_conditional_edges("batch_emails",fan_out_batches,["process_batch"])
workflow.add_edge("process_batch",END)
# class RouterAgent:
#     def __init__(self,llm_provider,
#         model_name: str,
#         prompt_version: str,
#         cache_enabled: bool = True,):
        
#         self.llm_provider = llm_provider
#         self.model_name = model_name
#         self.prompt_version = prompt_version
#         self.cache_enabled = cache_enabled
#         self.agent_name = self.__class__.__name__
        
#     def decide(self,cache,llm,emails:List[EmailObject],prev_summary: List[str]):
        
        