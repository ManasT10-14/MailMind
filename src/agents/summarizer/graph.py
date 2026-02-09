from src.agents.summarizer.state import SummarizerState
from langgraph.graph import StateGraph,START,END
from src.agents.summarizer.nodes import summarize


def build_graph():
    workflow = StateGraph(state_schema=SummarizerState)
    workflow.add_node("summarize",summarize)
    workflow.add_edge(START,"summarize")
    workflow.add_edge("summarize",END)
    
    agent = workflow.compile()
    
    return agent