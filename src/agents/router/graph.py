from src.prompts.router_agent_prompt import SYSTEM_PROMPT_ROUTER_AGENT,PROMPT_VERSION_ROUTER_AGENT,build_router_agent_prompt
from src.llm.service import call_llm_cached
from src.schema.email_object import EmailObject
from src.agents.router.state import RouterState
from typing import List,TypedDict,Dict,Literal,Any,Annotated
from operator import or_
from langgraph.graph import StateGraph,START,END
from langgraph.types import Command,Send
from src.ingestion.batching import batch_by_sender_and_time

from src.agents.router.nodes import batch_emails,fan_out_batches,process_batch

def build_graph():
    workflow = StateGraph(state_schema=RouterState)
    workflow.add_node("batch_emails",batch_emails)
    workflow.add_node("fan_out_batches",fan_out_batches)
    workflow.add_node("process_batch",process_batch)

    workflow.add_edge(START,"batch_emails")
    workflow.add_conditional_edges("batch_emails",fan_out_batches,["process_batch"])
    workflow.add_edge("process_batch",END)

    agent = workflow.compile()
    return agent