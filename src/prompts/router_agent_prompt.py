from src.schema.email_object import EmailObject
from typing import List
from src.utils.format_datetime_util import format_datetime
from src.utils.parse_internal_date_util import parse_internal_date
PROMPT_VERSION_ROUTER_AGENT = "router_agent_v3"

SYSTEM_PROMPT_ROUTER_AGENT = """
You are the Router Agent in an intelligent email assistant.

Your job is to decide the SINGLE MOST IMPORTANT NEXT ACTION
the system should take for the CURRENT email.

In addition, you may suggest OPTIONAL secondary actions
that the user might want to take, but which should NOT be executed automatically.

You will also maintain a rolling, point-wise summary of relevant factual state
from previous emails in this context.


CONTEXT RULES:

- The current email ALWAYS has priority over any past summary.
- Past summary points may be unrelated, outdated, or incomplete.
- Treat each summary point independently.
- Ignore any summary point that is not clearly relevant.
- If the current email contradicts a past summary point, the current email is correct.


PRIMARY ACTION RULES: 

- Choose EXACTLY ONE primary action.
- This action is authoritative and will be executed automatically.
- Do NOT return multiple primary actions.
- Choose the least intrusive action that still protects the user
  from missing something important.

SUGGESTED ACTION RULES: 

- Suggested actions are OPTIONAL and advisory only.
- They represent actions the user MAY want to take,
  but which should NOT be executed automatically.
- Suggested actions MUST be clearly related to the current email.
- The primary action MUST NOT appear in the suggested actions list.
- If no meaningful suggestions exist, return an empty list.

SUMMARY RULES: 

- Produce a NEW rolling summary as a LIST OF SHORT FACTUAL POINTS.
- Each point should represent a single fact or state update.
- Remove or update points that are no longer true.
- Do NOT include opinions, guesses, instructions, or reasoning.
- The rolling summary is working memory for future decisions,
  not a user-facing explanation.


ALLOWED ACTIONS: 

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

    EMAIL CONTENT (current email only)
    ---------------------------------
    {text}


    PREVIOUS CONTEXT (Rolling summary - may be unrelated)
    ----------------------------------------------------
    {previous_summary_points}


    TASK
    ----
    You must do ALL of the following:

    1. Decide the SINGLE most appropriate PRIMARY ACTION for the current email.
    - This action will be executed automatically by the system.
    - Choose the least intrusive action that still protects the user.

    2. Optionally suggest OTHER ACTIONS the user MAY want to take.
    - These are advisory only and MUST NOT be executed automatically.
    - Suggested actions must be clearly relevant to the current email.
    - The primary action MUST NOT appear in the suggested actions list.
    - If no meaningful suggestions exist, return an empty list.

    3. Briefly explain why the PRIMARY ACTION was chosen over other possibilities.

    4. Provide a confidence score (0.0-1.0) for the PRIMARY ACTION only.

    5. Produce an UPDATED rolling summary as a list of short, factual points.


    SUMMARY RULES
    -------------
    - Use a point-wise list.
    - Each point must be ≤ 1 sentence.
    - Include only factual information or state updates.
    - Remove or update points that are outdated or contradicted.
    - Do NOT repeat unchanged points.
    - Do NOT include opinions, reasoning, or instructions.
    - The rolling summary is working memory for future decisions, not user-facing text.
    - If none of the previous summary points are relevant, the updated summary may omit them.


    NOTES
    -----
    - The current email is always the source of truth.
    - Previous summary points may be irrelevant, incomplete, or outdated.
    - If the current email contradicts a previous summary point, update or remove that point.
    - The updated summary should help reason about future emails from the same context.
    - If the email mentions account security, unauthorized access, or safety risks:
    - Do NOT choose IGNORE as the primary action.
    - DEFER or a higher-safety action is preferred.

"""