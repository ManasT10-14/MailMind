from src.prompts.draft_reply_prompt import PROMPT_VERSION_DRAFT_REPLY,SYSTEM_PROMPT_DRAFT_AGENT,build_draft_reply_prompt
from src.llm.service import call_llm_cached
from src.schema.draft_reply_schema import DraftReplySchema
from src.config import MODEL_NAME
from src.agents.draft_reply.state import DraftState


def draft_reply(state:DraftState) -> dict:
    context_summary = state.get("context_summary")
    email = state["email"]
    reply_prompt = build_draft_reply_prompt(email=email,context_summary=context_summary)
    result: DraftReplySchema = call_llm_cached(cache=state["cache"],llm=state["llm"],provider=state["provider"],model_name=MODEL_NAME,system_prompt=SYSTEM_PROMPT_DRAFT_AGENT,user_prompt=reply_prompt,output_schema=DraftReplySchema,prompt_version=PROMPT_VERSION_DRAFT_REPLY,agent_name="DraftReplyAgent",cache_enabled=True)

    return {"reply":result}