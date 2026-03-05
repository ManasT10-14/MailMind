from typing import Dict,Any,List
from src.schema.email_object import EmailObject
from src.schema.summarizer_schema import SummarizerSchema
from src.schema.calendar_event_schema import CalendarEventSchema
from src.schema.draft_reply_schema import DraftReplySchema
from src.pipeline.state import UserDecision

def build_initial_state(*,start_date:str,end_date:str,summaries:Dict[str,SummarizerSchema],drafts:Dict[str,DraftReplySchema],calendar_events:Dict[str,CalendarEventSchema],approved_actions:Dict[str,bool],hitl_queue: List[str],hitl_index:int,defer:bool,cache:Any,llm:Any,provider:Any,embedding_model:Any,user_decision:UserDecision,trace:List[str]) -> Dict[str,Any]:

    return {
        "start_date": start_date,
        "end_date": end_date,
        "summaries": summaries,
        "drafts": drafts,
        "calendar_events": calendar_events,
        "approved_actions": approved_actions,
        "hitl_queue": hitl_queue,
        "hitl_index": hitl_index,
        "defer": defer,
        "cache":cache,
        "llm":llm,
        "provider":provider,
        "embedding_model":embedding_model,
        "user_decision":user_decision,
        "trace":trace
    }

