from pydantic import BaseModel,Field
from typing import Dict,List,Literal


class RouterSchema(BaseModel):
    action: Literal["IGNORE","SUMMARIZE","DRAFT_REPLY","ADD_TO_CALENDAR","DEFER"] = Field(...,description="Based on the provided email select the appropriate action.")
    explanation: str = Field(...,description="Explain the reason around the choice of action.")
    confidence: float = Field(...,description="Give the confidence score for your decesion.",ge=0,le=5)
    rolling_summary: List[str] = Field(...,description="The summary of some messages which might be related to this email.")