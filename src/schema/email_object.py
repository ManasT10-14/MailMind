from pydantic import BaseModel,Field
from typing import Dict,List,Literal



class Metadata(BaseModel):
    sender : str
    to : List[str]
    subject : str
    date: str
    labels: List[str]
    internal_timestamp: int 
class NormalizedContent(BaseModel):
    text: str
    paragraphs: List[str] 
class Intent(BaseModel):
    email_type: Literal["newsletter","notification","transactional","personal"]
    source: str = "heuristic"
    confidence: float | None = None
    
class Content(BaseModel):
    cleaned_text: NormalizedContent
    
class EmailObject(BaseModel):
    message_id: str
    thread_id: str
    
    metadata: Metadata
    intent: Intent
    content: Content
    
    attachments: List[dict] = []
    
    