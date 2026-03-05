from fastapi import FastAPI
from uuid import uuid4
from src.pipeline.graph import build_graph
from src.utils.build_parent_init_state import build_initial_state as build_parent_initial_state
from src.config import cache,llm,provider,embedding_model
from src.pipeline.state import UserDecision
from pydantic import BaseModel


app = FastAPI()

SESSION_STORE = {}
parent_graph = build_graph()


class StartRequest(BaseModel):
    start_date: str
    end_date: str


class ResumeRequest(BaseModel):
    session_id: str
    user_decision: UserDecision

@app.post("/start")
def start_pipeline(request: StartRequest):

    session_id = str(uuid4())

    initial_state = build_parent_initial_state(start_date=request.start_date,end_date=request.end_date,summaries={},drafts={},calendar_events={},approved_actions={},hitl_queue=[],hitl_index=0,defer=False,llm=llm,cache=cache,provider=provider,embedding_model=embedding_model,user_decision=None)

    result = parent_graph.invoke(initial_state)

    # Case 1 — waiting for HITL
    if result.get("status") == "WAITING_FOR_USER":
        SESSION_STORE[session_id] = result
        return {
            "session_id": session_id,
            "status": "WAITING_FOR_USER",
            "payload": result["hitl_payload"],
            "trace": result.get("trace", [])
        }

    # Case 2 — no HITL required
    return {
        "session_id": session_id,
        "status": "COMPLETED",
        "summaries": result.get("summaries", {}),
        "drafts": result.get("drafts", {}),
        "calendar_events": result.get("calendar_events", {}),
        "trace": result.get("trace", [])
    }
@app.post("/resume")
def resume_workflow(request: ResumeRequest):

    session_id = request.session_id

    if session_id not in SESSION_STORE:
        return {"error": "Invalid session_id"}

    state = SESSION_STORE[session_id]
    state["user_decision"] = request.user_decision.model_dump()

    result = parent_graph.invoke(state)

    if result.get("status") == "WAITING_FOR_USER":
        SESSION_STORE[session_id] = result

        return {
            "session_id": session_id,
            "status": "WAITING_FOR_USER",
            "payload": result["hitl_payload"],
            "trace": result.get("trace", [])
        }

    del SESSION_STORE[session_id]

    return {
    "session_id": session_id,
    "status": "COMPLETED",
    "summaries": result.get("summaries", {}),
    "drafts": result.get("drafts", {}),
    "calendar_events": result.get("calendar_events", {}),
    "trace": result.get("trace", [])
    }