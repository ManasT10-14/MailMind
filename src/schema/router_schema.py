from pydantic import BaseModel,Field
from typing import Dict,List,Literal

from pydantic import BaseModel, Field
from typing import List, Literal

ActionType = Literal[
    "IGNORE",
    "SUMMARIZE",
    "DRAFT_REPLY",
    "ADD_TO_CALENDAR",
    "DEFER",
]

class RouterSchema(BaseModel):
    action: ActionType = Field(
        ...,
        description=(
            "The SINGLE primary action the system should take for this email. "
            "This action is authoritative and will be executed automatically."
        ),
    )

    suggested_actions: List[ActionType] = Field(
        default_factory=list,
        description=(
            "Optional advisory actions that the user MAY want to take in addition "
            "to the primary action. These are suggestions only and are NOT executed "
            "automatically. The primary action MUST NOT appear here."
        ),
    )

    explanation: str = Field(
        ...,
        description=(
            "A concise explanation justifying why the primary action was chosen "
            "over other possible actions."
        ),
    )

    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description=(
            "Confidence score for the primary action decision. "
            "Used to determine whether human review or deferral is appropriate."
        ),
    )

    rolling_summary: List[str] = Field(
        ...,
        description=(
            "Updated rolling, point-wise summary representing the current factual "
            "state across related emails. Each item should be a short, factual statement "
            "used as working memory for future routing decisions."
        ),
    )
