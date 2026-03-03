from fastapi import FastAPI
from uuid import uuid4
from src.pipeline imo
app = FastAPI()

SESSION_STORE = {}

@app.post("/start")
def start_pipeline(request: dict):

    session_id = str(uuid4())

    initial_state = {
        "start_date": request["start_date"],
        "end_date": request["end_date"],
        "summaries": {},
        "drafts": {},
        "calendar_events": {},
        "approved_actions": {},
        "hitl_queue": [],
        "hitl_index": 0,
        "defer": False,
        # include llm, cache, provider, embedding_model here
    }

    result = parent_graph.invoke(initial_state)

    # Case 1 — waiting for HITL
    if result.get("status") == "WAITING_FOR_USER":
        SESSION_STORE[session_id] = result
        return {
            "session_id": session_id,
            "status": "WAITING_FOR_USER",
            "hitl_payload": result["hitl_payload"]
        }

    # Case 2 — no HITL required
    return {
        "session_id": session_id,
        "status": "COMPLETED",
        "result": result
    }