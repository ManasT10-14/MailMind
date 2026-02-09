from src.agents.router.state import RouterState
from langgraph.graph import StateGraph,START,END
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