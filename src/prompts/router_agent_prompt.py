from src.schema.email_object import EmailObject
from typing import List
from src.utils.format_datetime_util import format_datetime
from src.utils.parse_internal_date_util import parse_internal_date
PROMPT_VERSION_ROUTER_AGENT = "router_agent_v1"

SYSTEM_PROMPT_ROUTER_AGENT = """
You are the Router Agent in an intelligent email assistant.

Your job is to decide the SINGLE MOST IMPORTANT NEXT ACTION
the system should take for the CURRENT email.

You will also maintain a rolling, point-wise summary of relevant facts
from previous emails in this context.

IMPORTANT RULES:
- The current email ALWAYS has priority over any past summary.
- The past summary may contain unrelated or outdated points.
- Treat each summary point independently.
- Ignore any summary point that is not clearly relevant.
- If the current email contradicts a past summary point, the current email is correct.

ACTION SELECTION RULES:
- Choose EXACTLY ONE primary action.
- Do NOT return multiple actions.
- Secondary actions may happen implicitly downstream.
- Choose the least intrusive action that still protects the user.

SUMMARY RULES:
- Produce a NEW rolling summary as a LIST OF SHORT FACTUAL POINTS.
- Each point should represent a single fact or state update.
- Remove or update points that are no longer true.
- Do NOT include opinions, guesses, or instructions.

Allowed actions:
- IGNORE
- SUMMARIZE
- DRAFT_REPLY
- ADD_TO_CALENDAR
- DEFER
"""

def build_router_agent_prompt(*,email:EmailObject,prev_summary:List[str]):
    sender = email.metadata.sender
    subject = email.metadata.subject
    timestamp = format_datetime(parse_internal_date(email.metadata.internal_timestamp))
    paragraph = email.content.cleaned_text.paragraphs
    text = """"""
    previous_summary_points = """"""
    for num,para in enumerate(prev_summary):
        previous_summary_points+=f"[S{num+1}] {para}\n"
    for num,para in enumerate(paragraph):
        text+=f"[P{num+1}] {para}\n"


    if previous_summary_points == "":
        previous_summary_points = "No prior context"
        
    return f"""
    CURRENT EMAIL
    --------------
    Sender: {sender}
    Subject: {subject}
    Time: {timestamp}

    Content:
    {text}


    PREVIOUS CONTEXT (Point-wise rolling summary - may be unrelated)
    --------------------------------------------
    {previous_summary_points}


    TASK
    ----
    1. Decide the SINGLE most appropriate NEXT ACTION for the current email.
    2. Briefly explain your reasoning.
    3. Provide a confidence score for your decision.
    4. Produce an UPDATED rolling summary as a list of short, factual points.

    SUMMARY RULES:
    - Point-wise list
    - Each point ≤ 1 sentence
    - Facts/state only
    - Remove outdated points
    - Do not repeat unchanged points    
    - The rolling summary is working memory for future decisions, not a user-facing summary.
    - If none of the previous summary points are relevant, the updated summary may omit them.
    
    NOTES:
    - The current email is the source of truth.
    - Some previous summary points may be irrelevant.
    - Remove or update summary points if they are outdated or contradicted.
    - The updated summary should help reason about future emails.
"""