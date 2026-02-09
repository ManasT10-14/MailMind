from langchain_openai import ChatOpenAI
import os
from src.llm.cache import SQLiteLLMCache
from src.config import DB_PATH
from src.llm.providers.gpt import OpenAIProvider
from src.config import MODEL_NAME
from src.ingestion.pipeline import read_emails_in_date_range
from src.agents.summarizer.graph import build_graph
from dotenv import load_dotenv
load_dotenv()

def build_initial_state(*,
    model_name = MODEL_NAME):
    
    cache = SQLiteLLMCache(db_path=DB_PATH)

    llm = ChatOpenAI(base_url="https://openrouter.ai/api/v1",model="openai/gpt-oss-120b",api_key=os.getenv("OPENROUTER_API_KEY"))

    provider = OpenAIProvider()

    return {
        "cache": cache,
        "llm": llm,
        "provider": provider,
        
    }
    
init_state = build_initial_state()
emails = read_emails_in_date_range("2026-02-1","2026-02-2")
email = emails[2]
init_state["email"] = email

agent = build_graph()

result = agent.invoke(init_state)
print(result)