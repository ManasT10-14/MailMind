from src.agents.calendar.state import CalendarState
from langgraph.graph import StateGraph,START,END
from src.agents.calendar.nodes import extract_event


def build_graph():
    workflow = StateGraph(state_schema=CalendarState)
    workflow.add_node("extract_event",extract_event)
    workflow.add_edge(START,"extract_event")
    workflow.add_edge("extract_event",END)
    
    agent = workflow.compile()
    
    return agent