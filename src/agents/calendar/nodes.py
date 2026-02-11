from src.prompts.calendar_event_prompt import PROMPT_VERSION_CALENDAR_AGENT,SYSTEM_PROMPT_CALENDAR_AGENT,build_calendar_agent_prompt
from src.llm.service import call_llm_cached
from src.schema.calendar_event_schema import CalendarEventSchema
from src.config import MODEL_NAME
from src.agents.calendar.state import CalendarState


def extract_event(state: CalendarState) -> dict:
    email = state["email"]
    reply_prompt = build_calendar_agent_prompt(email=email)
    result: CalendarEventSchema = call_llm_cached(cache=state["cache"],llm=state["llm"],provider=state["provider"],model_name=MODEL_NAME,system_prompt=SYSTEM_PROMPT_CALENDAR_AGENT,user_prompt=reply_prompt,output_schema=CalendarEventSchema,prompt_version=PROMPT_VERSION_CALENDAR_AGENT,agent_name="CalendarAgent",cache_enabled=True)
    
    return {"event_details":result}