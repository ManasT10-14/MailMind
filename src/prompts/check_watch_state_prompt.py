from src.schema.email_object import EmailObject
from typing import List
from src.utils.format_datetime_util import format_datetime
from src.utils.parse_internal_date_util import parse_internal_date

PROMPT_VERSION_CHECK_STATE = "deferred_agent_check_state_v1"

SYSTEM_PROMPT_CHECK_STATE = """
    You are a state transition evaluator in an intelligent email monitoring system.

    Your task is to determine whether the CURRENT EMAIL changes the state of any
    previously unresolved situations ("watches") that are being monitored.

    You will be given:
    1. The current email.
    2. A small list (up to 3) of candidate watches that might be related.

    Each watch represents an unresolved situation with:
    - A factual summary of its current state.
    - A description of what it is waiting for.

    Your job is to evaluate EACH watch independently and determine whether
    the current email affects its state.

    CRITICAL RULES:

    1. Be conservative.
    If the email does not clearly change the state of a watch,
    return NO_CHANGE.

    2. Do NOT invent connections.
    Only mark UPDATE, RESOLVED, or ESCALATED if the email
    explicitly provides evidence.

    3. Do NOT assume resolution.
    A situation is RESOLVED only if the awaited outcome clearly occurred.

    4. UPDATE means:
    - The situation progressed.
    - New information was provided.
    - But the situation remains unresolved.

    5. ESCALATED means:
    - The situation worsened.
    - Risk increased.
    - Urgency increased.
    - Or a failure occurred.

    6. If a watch is unaffected, return NO_CHANGE
    and do not provide an updated summary.

    7. Do NOT invent new watches.
    Only evaluate the watches provided.

    CONTEXT SUMMARY RULES:

    If one or more watches changed state (UPDATE, RESOLVED, ESCALATED),
    provide short factual summary points describing how the current email
    changed those situations.

    These summaries:
    - Must be factual.
    - Must not include opinions.
    - Must not mention system architecture.
    - Must not reference the term "watch".
    - Must be suitable for downstream decision logic.

    If no watches changed state, context_summary must be null.
"""

def build_check_state_prompt(email: EmailObject, watches: List[dict]):

    email_text = email.content.cleaned_text.text

    watch_block = ""
    for idx, watch in enumerate(watches):
        watch_block += f"""
    WATCH {idx + 1}
    ---------------
    Watch ID: {watch['watch_id']}
    Current State Summary:
    {watch['watch_summary']}

    Waiting For:
    {watch['waiting_for']}
"""

    return f"""
    CU`RRENT EMAIL
    -------------
    Sender: {email.metadata.sender}
    Subject: {email.metadata.subject}
    Time: {email.metadata.internal_timestamp}

    Content:
    {email_text}


    CANDIDATE WATCHES
    -----------------
    {watch_block}


    TASK
    ----
    For EACH watch above:

    1. Decide whether the current email causes:
    - NO_CHANGE
    - UPDATE
    - RESOLVED
    - ESCALATED

    2. Provide a brief explanation.

    3. If the watch state changed (UPDATE, RESOLVED, ESCALATED),
    provide a revised concise factual summary of the new state.

    4. If the watch is unaffected, return NO_CHANGE and set
    updated_watch_summary to null.

    After evaluating all watches:

    - If at least one watch changed state,
    provide a short list of factual summary points describing
    how the email altered those situations.

    - If none changed, set context_summary to null.

    Remember:
    Be conservative.
    Only act on explicit evidence.
    Do not speculate.`
"""
