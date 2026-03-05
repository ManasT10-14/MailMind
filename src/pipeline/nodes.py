from langgraph.graph import StateGraph,END
from src.pipeline.state import ParentState
from src.ingestion.pipeline import read_emails_in_date_range
from src.schema.email_object import EmailObject
from src.agents.router.graph import build_graph as build_router
from typing import List,Annotated,Literal
from src.utils.build_router_init_state import (
    build_initial_state as build_router_init_state,
)
from langgraph.types import Send, Command
from src.schema.router_schema import RouterSchema
from src.agents.defer.graph import build_graph as build_defer
from src.utils.build_defer_init_state import (
    build_initial_state as build_defer_init_state,
)

from src.agents.summarizer.graph import build_graph as build_summarizer
from src.utils.build_summarizer_init_state import build_initial_state as build_summarizer_init_state

from src.agents.draft_reply.graph import build_graph as build_draft_reply
from src.utils.build_draft_reply_init_state import build_initial_state as build_draft_reply_init_state

from src.agents.calendar.graph import build_graph as build_calendar
from src.utils.build_calendar_init_state import build_initial_state as build_calendar_init_state

router_agent = build_router()
defer_agent = build_defer()
summarizer_agent = build_summarizer()
draft_agent = build_draft_reply()
calendar_agent = build_calendar()


def entry_pipeline(state:ParentState) -> Command[Literal["fetch_emails","process_user_decision"]]:
    if state.get("user_decision") is not None:
        return Command(goto="process_user_decision")
    return Command(goto="fetch_emails")

def fetch_emails(state: ParentState):
    start_date = state["start_date"]
    end_date = state["end_date"]
    emails: List[EmailObject] = read_emails_in_date_range(
        start_date=start_date, end_date=end_date
    )
    emails = sorted(emails, key=lambda email: email.metadata.internal_timestamp)
    trace = state.get("trace", [])
    trace.append(f"Fetched {len(emails)} emails")
    return {"emails": emails, "current_index": 0, "actions": {},"trace":trace}


def run_router_batch(state: ParentState):

    llm = state["llm"]
    cache = state["cache"]
    provider = state["provider"]
    actions = {}

    emails = state["emails"]
    defer_context = None

    router_init_state: dict = build_router_init_state(
        cache=cache,
        llm=llm,
        provider=provider,
        emails=emails,
        actions=actions,
        defer=False,
        defer_context=defer_context,
    )

    router_result: dict = router_agent.invoke(router_init_state)

    trace = state.get("trace", [])
    trace.append("Router processed batch")
    return {"actions": router_result["actions"],"trace":trace}


def init_defer_loop(state: ParentState):
    return {"current_index": 0}


def run_router_defer(state: ParentState) -> Command[Literal["process_defer"]]:

    llm = state["llm"]
    cache = state["cache"]
    provider = state["provider"]

    current_index = state["current_index"]
    email = state["emails"][current_index]

    context_summary = state["defer_context"]

    router_init_state = build_router_init_state(
        cache=cache,
        llm=llm,
        provider=provider,
        emails=[email],
        actions={},
        defer_context=context_summary,
        defer=True,
    )

    router_result = router_agent.invoke(router_init_state)

    new_action = router_result["actions"][email.message_id]

    updated_actions = dict(state["actions"])
    updated_actions[email.message_id] = new_action

    return Command(
        goto="process_defer",
        update={
            "actions": updated_actions,
            "defer_context": None,
            "current_index": current_index + 1,
        },
    )


def process_defer(state: ParentState) -> Command[Literal["dispatcher","process_defer","run_router_defer"]]:
    total_emails = len(state["emails"])
    current_index = state["current_index"]
    trace = state.get("trace", [])
    trace.append(f"Defer checking email {email.message_id}")
    if (
        current_index >= total_emails
    ):  # because index starts from 0 so if it is equal to total_emails it means we have exceeded the total emails range so we move to next step
        return Command(goto="dispatcher")
    llm = state["llm"]
    cache = state["cache"]
    provider = state["provider"]
    embedding_model = state["embedding_model"]
    email = state["emails"][current_index]
    action = state["actions"].get(email.message_id)
    if not action:
        return Command(
            goto="process_defer", update={"current_index": current_index + 1}
        )

    defer_init_state: dict = build_defer_init_state(
        cache=cache,
        llm=llm,
        provider=provider,
        embedding_model=embedding_model,
        email=email,
        action=action,
    )

    defer_result = defer_agent.invoke(defer_init_state)

    if defer_result["run_router"]:
        return Command(
            goto="run_router_defer",
            update={"defer_context": defer_result["router_summary"],"trace":trace},
        )

    return Command(goto="process_defer", update={"current_index": current_index + 1,"trace":trace})


def dispatcher(state: ParentState):
    emails = state["emails"]
    actions = state["actions"]
    cache = state["cache"]
    llm = state["llm"]
    provider = state["provider"]

    workers = []

    for email in emails:
        action_obj = actions.get(email.message_id)
        if not action_obj:
            continue

        if action_obj.action == "ADD_TO_CALENDAR":
            workers.append(
                Send(
                    "add_to_calendar",
                    {
                        "email": email,
                        "cache": cache,
                        "llm": llm,
                        "provider": provider,
                    },
                )
            )

        elif action_obj.action == "SUMMARIZE":
            workers.append(
                
                Send(
                    "summarizer",
                    {
                        "email": email,
                        "cache": cache,
                        "llm": llm,
                        "provider": provider,
                    },
                )
            )

        elif action_obj.action == "DRAFT_REPLY":
            workers.append(
                Send(
                    "draft_reply",
                    {
                        "email": email,
                        "context_summary": action_obj.rolling_summary,
                        "cache": cache,
                        "llm": llm,
                        "provider": provider,
                    },
                )
            )
    trace = state.get("trace", [])
    trace.append(f"Dispatcher created {len(workers)} workers")
    return workers



def summarize(state: ParentState):
    email:EmailObject = state["email"]
    cache = state["cache"]
    llm = state["llm"]
    provider = state["provider"]
    init_state = build_summarizer_init_state(cache=cache,llm=llm,provider=provider,email=email)
    summarizer_result = summarizer_agent.invoke(init_state)
    
    summary = {email.message_id:summarizer_result["summary"]}

    return {"summaries":summary}

def draft_reply(state: ParentState):
    email:EmailObject = state["email"]
    cache = state["cache"]
    llm = state["llm"]
    provider = state["provider"]
    context_summary = state["context_summary"]
    
    init_state = build_draft_reply_init_state(cache=cache,llm=llm,provider=provider,email=email,context_summary=context_summary)
    draft_result = draft_agent.invoke(init_state)
    
    draft = {email.message_id:draft_result["reply"]}
    
    return {"drafts":draft}
    
def add_to_calendar(state:ParentState):
    email:EmailObject = state["email"]
    cache = state["cache"]
    llm = state["llm"]
    provider = state["provider"]

    
    init_state = build_calendar_init_state(cache=cache,llm=llm,provider=provider,email=email)
    calendar_result = calendar_agent.invoke(init_state)
    
    events = {email.message_id:calendar_result["event_details"]}
    
    return {"calendar_events":events}


def post_dispatcher_node(state:ParentState) -> Command[Literal["hitl_review",END]]:
    drafts = state.get("drafts",{})
    calendar_events = state.get("calendar_events",{})
    emails = state["emails"]
    has_drafts = len(drafts) > 0
    has_calendar_events = len(calendar_events) > 0
    
    draft_email_ids = list(drafts.keys())
    calendar_email_ids = list(calendar_events.keys())
    hitl_queue: List[str] = []
    if has_drafts or has_calendar_events:
        for email in emails:
            if (email.message_id in draft_email_ids) or (email.message_id in calendar_email_ids):
                hitl_queue.append(email.message_id)
        
        return Command(goto="hitl_review",update={"hitl_queue":hitl_queue,"hitl_index":0})
    
    return Command(goto=END)

def hitl_review(state: ParentState) -> Command[Literal["execute_actions","await_user_decision"]]:
    queue = state["hitl_queue"]
    index = state["hitl_index"]
    
    if index >= len(queue):
        return Command(goto="execute_actions")
    
    current_email_id = queue[index]
    trace = state.get("trace", [])
    trace.append(f"HITL required for email {current_email_id}")
    return Command(goto="await_user_decision",update={"current_hitl_email":current_email_id,"trace":trace})


def await_user_decision(state:ParentState):
    message_id = state["current_hitl_email"]
    index = state["hitl_index"]
    queue = state["hitl_queue"]

    email_obj = next(
        e for e in state["emails"]
        if e.message_id == message_id
    )

    draft = state.get("drafts", {}).get(message_id)
    calendar_event = state.get("calendar_events", {}).get(message_id)

    payload = {
        "message_id": message_id,
        "original_email": email_obj,
        "position": {
            "current": index + 1,
            "total": len(queue)
        }
    }

    if draft is not None:
        payload["draft"] = draft
        payload["type"] = "draft"
    else:
        payload["calendar_event"] = calendar_event
        payload["type"] = "calendar_event"
    return {
        "status": "WAITING_FOR_USER",
        "hitl_payload": payload
    }
    
def process_user_decision(state: ParentState) -> Command[Literal["hitl_review"]]:

    decision = state["user_decision"]
    message_id = decision["message_id"]

    drafts = dict(state.get("drafts", {}))
    calendar_events = dict(state.get("calendar_events", {}))
    approved_actions = dict(state.get("approved_actions", {}))

    if decision["approved"]:
        if decision["type"] == "draft":
            if decision.get("edited_draft"):
                drafts[message_id] = decision["edited_draft"]

        elif decision["type"] == "calendar_event":
            if decision.get("edited_calendar_event"):
                calendar_events[message_id] = decision["edited_calendar_event"]

    approved_actions[message_id] = decision["approved"]

    return Command(
        goto="hitl_review",
        update={
            "drafts": drafts,
            "calendar_events": calendar_events,
            "approved_actions": approved_actions,
            "hitl_index": state["hitl_index"] + 1,
            "user_decision": None,
        }
    )
def execute_actions(state: ParentState) -> Command[Literal[END]]:

    approved = state.get("approved_actions", {})

    for message_id, decision in approved.items():

        if not decision["approved"]:
            continue

        if message_id in state.get("drafts", {}):
            pass

        if message_id in state.get("calendar_events", {}):

            pass
        
    
    trace = state.get("trace", [])    
    trace.append(f"Executed approved actions")

    return Command(goto=END,update={"trace":trace})