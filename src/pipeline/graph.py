from langgraph.graph import StateGraph,START,END
from src.pipeline.state import ParentState
from src.pipeline.nodes import *
def build_graph():
    graph = StateGraph(state_schema=ParentState)
    graph.add_node("entry_pipeline",entry_pipeline)
    graph.add_node("fetch_emails",fetch_emails)
    graph.add_node("run_router_batch",run_router_batch)
    graph.add_node("init_defer_loop",init_defer_loop)
    graph.add_node("run_router_defer",run_router_defer)
    graph.add_node("process_defer",process_defer)
    graph.add_node("dispatcher",dispatcher)
    graph.add_node("summarizer",summarize)
    graph.add_node("draft_reply",draft_reply)
    graph.add_node("add_to_calendar",add_to_calendar)
    graph.add_node("post_dispatcher_node",post_dispatcher_node)
    graph.add_node("hitl_review",hitl_review)
    graph.add_node("await_user_decision",await_user_decision)
    graph.add_node("process_user_decision",process_user_decision)
    graph.add_node("execute_actions",execute_actions)
    
    graph.add_edge(START,"entry_pipeline")
    graph.add_edge("fetch_emails","run_router_batch")
    graph.add_edge("run_router_batch","init_defer_loop")
    graph.add_edge("init_defer_loop","process_defer")
    graph.add_conditional_edges("process_defer",dispatcher,["add_to_calendar","summarizer","draft_reply"])
    graph.add_edge("summarizer","post_dispatcher_node")
    graph.add_edge("add_to_calendar","post_dispatcher_node")
    graph.add_edge("draft_reply","post_dispatcher_node")
    
    workflow = graph.compile()

    png_bytes = workflow.get_graph().draw_mermaid_png()
    with open("workflow.png", "wb") as f:
        f.write(png_bytes)

    return workflow

build_graph() 