from pydantic import BaseModel, Field
from typing import Optional, Literal


class DraftReplySchema(BaseModel):
    subject: Optional[str] = Field(
        None,
        description=(
            "Optional revised subject line for the reply. "
            "Only provide this if the original subject is unclear, missing, "
            "or requires modification (e.g., adding 'Re:' context). "
            "Otherwise return null."
        ),
    )

    body: str = Field(
        ...,
        description=(
            "The complete email reply body, ready to send. "
            "It must be professionally written, coherent, and directly "
            "address the content of the original email. "
            "Do not invent facts, commitments, attachments, or information "
            "that were not explicitly present in the email."
        ),
    )

    tone: Literal[
        "professional",
        "formal",
        "neutral",
        "friendly",
        "assertive"
    ] = Field(
        ...,
        description=(
            "The dominant communication tone used in the drafted reply. "
            "Select the tone that best represents the style of writing. "
            "This is used for internal preference learning and consistency tracking."
        ),
    )

    key_points_addressed: Optional[list[str]] = Field(
        default=None,
        description=(
            "Optional short list of the main points from the original email "
            "that were addressed in the reply. Each item should be concise "
            "and factual. This helps verify coverage and reduces hallucination risk."
        ),
    )

    confidence: float = Field(
        ...,
        ge=0,
        le=1,
        description=(
            "Confidence score between 0 and 1 indicating how certain the model "
            "is that the drafted reply correctly addresses the email without "
            "missing required information or making assumptions."
        ),
    )
