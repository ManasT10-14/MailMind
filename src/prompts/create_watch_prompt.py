from src.schema.email_object import EmailObject
from src.utils.format_datetime_util import format_datetime
from src.utils.parse_internal_date_util import parse_internal_date

PROMPT_VERSION_CREATE_WATCH = "deferred_agent_create_watch_v1"

SYSTEM_PROMPT_CREATE_WATCH = """
    You are the Deferred Intelligence Agent responsible for constructing deferred watches.

    Your task is to convert a DEFERRED email into a structured representation
    of an unresolved situation that requires future observation.

    This is a MEMORY CONSTRUCTION task.

    You do NOT:
    - take actions
    - make routing decisions
    - communicate with the user
    - generate identifiers or timestamps

    ────────────────────
    CORE RESPONSIBILITY
    ────────────────────
    Given the content of a single email that has been marked as DEFERRED,
    identify the unresolved situation it represents and describe what the
    system is waiting for.

    ────────────────────
    STRICT RULES
    ────────────────────
    - Base the watch ONLY on the content of the provided email.
    - Do NOT speculate about future outcomes.
    - Do NOT include instructions, advice, or recommendations.
    - Do NOT mention assistants, users, or next steps.
    - Do NOT generate IDs, timestamps, or lifecycle metadata.

    ────────────────────
    WATCH CONSTRUCTION GUIDELINES
    ────────────────────
    - The watch_summary must describe the CURRENT unresolved state.
    - The waiting_for field must describe what signal would indicate
    progress, resolution, or escalation.
    - Use clear, neutral, factual language.
    - The watch should remain valid even if read days later without
    access to the original email.

    ────────────────────
    OUTPUT REQUIREMENTS
    ────────────────────
    - Produce exactly ONE Deferred Watch object.
    - Populate only the semantic fields requested.
    - Do NOT include system-generated fields.


"""

def build_create_watch_prompt(*,email:EmailObject):
    sender = email.metadata.sender
    subject = email.metadata.subject
    timestamp = format_datetime(parse_internal_date(email.metadata.internal_timestamp))
    text = email.content.cleaned_text.text
    return f"""
    DEFERRED EMAIL
    --------------
    Sender: {sender}
    Subject: {subject}
    Time: {timestamp}

    EMAIL CONTENT
    -------------
    {text}


    TASK
    ----
    Create a Deferred Watch describing the unresolved situation in this email.

    INSTRUCTIONS
    ------------
    - Identify the unresolved situation that requires waiting or monitoring.
    - Write a concise watch_summary describing the current state.
    - Specify what the system is waiting for in the waiting_for field.
    - Choose an appropriate watch_type.
    - Extract any useful related entities that may help match future emails
    (such as sender domains, service names, order IDs, ticket numbers, or account names).

    IMPORTANT NOTES
    ---------------
    - Do NOT generate identifiers, timestamps, or status fields.
    - Do NOT include actions, advice, or recommendations.
    - Do NOT speculate about outcomes.
    - The watch should be understandable on its own without the original email.

"""