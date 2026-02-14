from langgraph.graph import StateGraph,START,END
from src.agents.defer.state import DeferState
from src.agents.defer.nodes import router,filter_watches,create_watch,check_state
def build_graph():
    workflow = StateGraph(state_schema=DeferState)
    workflow.add_node("router",router)
    workflow.add_node("filter_watches",filter_watches)
    workflow.add_node("create_watch",create_watch)
    workflow.add_node("check_state",check_state)
    
    workflow.add_edge(START,"router")
    
    agent = workflow.compile()
    
    return agent

if __name__ == "__main__":
    agent = build_graph()
    from IPython.display import Image, display
    from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

    display(Image(agent.get_graph().draw_mermaid_png()))