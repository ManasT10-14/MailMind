from pydantic import BaseModel, Field
from typing import Literal, List


class DeferredWatchSchema(BaseModel):
    # watch_id: str = Field(
    #     ...,
    #     description=(
    #         "A unique identifier for this deferred watch. "
    #         "Used to update, resolve, or delete this watch in long-term memory. "
    #         "Must remain stable across the lifetime of the watch."
    #     ),
    # )

    # source_email_id: str = Field(
    #     ...,
    #     description=(
    #         "The message_id of the email that originally caused this watch to be created. "
    #         "This is used for traceability and explanation of why the watch exists."
    #     ),
    # )

    watch_type: str = Field(
        ...,
        description=(
            "A coarse-grained category describing the nature of what is being monitored. "
            "Examples include security, delivery, application, payment, support_ticket, or general_wait. "
            "This helps guide how future emails are evaluated against this watch."
        ),
    )

    watch_summary: str = Field(
        ...,
        description=(
            "A concise, factual summary of the unresolved situation represented by this watch. "
            "This summary should capture the current state and be suitable for injecting into "
            "the Router agent as contextual memory. Do not include speculation or instructions."
        ),
    )

    waiting_for: str = Field(
        ...,
        description=(
            "A short description of what outcome, signal, or update would indicate progress, "
            "resolution, or escalation of this watch. "
            "Examples: 'delivery confirmation', 'follow-up response', 'approval or rejection', "
            "'security confirmation'."
        ),
    )

    # created_at: str = Field(
    #     ...,
    #     description=(
    #         "The timestamp indicating when this watch was created. "
    #         "Used for aging, expiration, and time-based escalation logic."
    #     ),
    # )

    # status: Literal["active", "resolved", "expired", "escalated"] = Field(
    #     ...,
    #     description=(
    #         "The current lifecycle state of this watch. "
    #         "'active' means it is still waiting for resolution. "
    #         "'resolved' means the awaited outcome has occurred. "
    #         "'expired' means it is no longer relevant due to time passing. "
    #         "'escalated' means the situation has worsened or requires user attention."
    #     ),
    # )

    related_entities: List[str] = Field(
        default_factory=list,
        description=(
            "Optional identifiers or entities related to this watch that help match future emails. "
            "Examples include sender domains, order IDs, ticket numbers, account names, or service names. "
            "These improve matching accuracy beyond raw semantic similarity."
        ),
    )
