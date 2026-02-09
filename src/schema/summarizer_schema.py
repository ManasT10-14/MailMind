from pydantic import BaseModel,Field
from typing import Dict,List,Literal

from pydantic import BaseModel, Field
from typing import List, Literal

class SummarizerSchema(BaseModel):
    overview: str = Field(
        ...,
        description=(
            "A concise, user-friendly one- to two-sentence overview of the email. "
            "It should capture the main purpose or message of the email without "
            "including unnecessary details."
        ),
    )

    bullet_points: List[str] = Field(
        default_factory=list,
        description=(
            "A point-wise summary of the key facts, updates, or information contained "
            "in the email. Each bullet point should be short, factual, and self-contained. "
            "Do not include opinions, instructions, or reasoning."
        ),
    )