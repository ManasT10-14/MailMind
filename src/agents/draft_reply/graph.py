from src.agents.draft_reply.state import DraftState
from langgraph.graph import StateGraph,START,END
from src.agents.draft_reply.nodes import draft_reply


def build_graph():
    workflow = StateGraph(state_schema=DraftState)
    workflow.add_node("draft_reply",draft_reply)
    workflow.add_edge(START,"draft_reply")
    workflow.add_edge("draft_reply",END)
    
    agent = workflow.compile()
    
    return agent