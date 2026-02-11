from pydantic import BaseModel, Field
from typing import Literal, List,Optional

class UpdateSchema(BaseModel):
    watch_summary: str = Field(
        ...,
        description=(
            "A concise, factual summary describing the new current state "
            "of the monitored situation after considering the current email. "
            "This must reflect the updated reality. "
            "Do not include opinions, speculation, or instructions."
        ),
    )

    waiting_for: str = Field(
        ...,
        description=(
            "A concise description of what outcome or signal is now being awaited. "
            "If the situation is RESOLVED, this should describe that no further action "
            "is required (e.g., 'No further action required'). "
            "If ESCALATED, this should reflect what is now expected or required next. "
            "If UPDATE, this should reflect the revised awaited outcome."
        ),
    )


class WatchStateDecision(BaseModel):
    watch_id: str = Field(
        ...,
        description=(
            "The unique identifier of the watch being evaluated."
        ),
    )

    decision: Literal["NO_CHANGE", "UPDATE", "RESOLVED", "ESCALATED"] = Field(
        ...,
        description=(
            "The state transition decision for this watch based on the current email. "
            "NO_CHANGE means the email does not affect this watch. "
            "UPDATE means the situation progressed but remains unresolved. "
            "RESOLVED means the awaited outcome clearly occurred. "
            "ESCALATED means the situation worsened or urgency increased."
        ),
    )

    explanation: str = Field(
        ...,
        description=(
            "A brief factual explanation of why this decision was made. "
            "Reference explicit signals from the current email and the previous watch state. "
            "Do not speculate."
        ),
    )

    updated_watch: Optional[UpdateSchema] = Field(
        None,
        description=(
            "If decision is UPDATE, RESOLVED, or ESCALATED, this field must contain "
            "the revised semantic state of the watch. "
            "If decision is NO_CHANGE, this field must be null. "
            "This field updates only the semantic content of the watch "
            "(watch_summary and waiting_for). Structural fields such as "
            "watch_id, watch_type, or related_entities must not be modified."
        ),
    )


class CheckStateSchema(BaseModel):
    watch_decisions: List[WatchStateDecision]

    context_summary: Optional[List[str]] = Field(
        None,
        description=(
            "If one or more watches changed state (UPDATE, RESOLVED, ESCALATED), "
            "provide short factual summary points describing how the current email "
            "altered those situations. These summaries will be used by downstream "
            "decision logic. If no watches changed state, this field must be null."
        ),
    )
