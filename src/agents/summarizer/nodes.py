from src.prompts.summarizer_agent_prompt import SYSTEM_PROMPT_SUMMARIZER_AGENT,PROMPT_VERSION_SUMMARIZER_AGENT,build_summarizer_agent_prompt
from src.llm.service import call_llm_cached
from src.schema.summarizer_schema import SummarizerSchema
from src.config import MODEL_NAME
from src.agents.summarizer.state import SummarizerState



def summarize(state: SummarizerState):
    email = state["email"]
    summarizer_prompt = build_summarizer_agent_prompt(email=email)
    result: SummarizerSchema = call_llm_cached(cache=state["cache"],llm=state["llm"],provider=state["provider"],model_name=MODEL_NAME,system_prompt=SYSTEM_PROMPT_SUMMARIZER_AGENT,user_prompt=summarizer_prompt,output_schema=SummarizerSchema,prompt_version=PROMPT_VERSION_SUMMARIZER_AGENT,agent_name="SummarizerAgent",cache_enabled=True)
    
    return {"summary":result}