from langgraph.graph import StateGraph
from src.pipeline.state import ParentState
from src.ingestion.pipeline import read_emails_in_date_range
from src.schema.email_object import EmailObject
from src.agents.router.graph import build_graph as build_router
from typing import List
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

router_agent = build_router()
defer_agent = build_defer()
summarizer_agent = build_summarizer()


def fetch_emails(state: ParentState):
    start_date = state["start_date"]
    end_date = state["end_date"]
    emails: List[EmailObject] = read_emails_in_date_range(
        start_date=start_date, end_date=end_date
    )
    emails = sorted(emails, key=lambda email: email.metadata.internal_timestamp)

    return {"emails": emails, "current_index": 0, "actions": {}}


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

    return {"actions": router_result["actions"]}


def init_defer_loop(state: ParentState):
    return {"current_index": 0}


def run_router_defer(state: ParentState):

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


def process_defer(state: ParentState):
    total_emails = len(state["emails"])
    current_index = state["current_index"]
    if (
        current_index >= total_emails
    ):  # because index starts from 0 so if it is equal to total_emails it means we have exceeded the total emails range so we move to next step
        return Command(goto="next_step")
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
            update={"defer_context": defer_result["router_summary"]},
        )

    return Command(goto="process_defer", update={"current_index": current_index + 1})


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
                    "summarize",
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

    return workers



def summarizer_worker(state: ParentState):
    email:EmailObject = state["email"]
    cache = state["cache"]
    llm = state["llm"]
    provider = state["provider"]
    init_state = build_summarizer_init_state(cache=cache,llm=llm,provider=provider,email=email)
    summarizer_result = summarizer_agent.invoke(init_state)
    
    summary = {email.message_id:summarizer_result["summary"]}
    
    return {"summaries":summary}