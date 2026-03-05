from pathlib import Path
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_openai import ChatOpenAI
from src.llm.cache import SQLiteLLMCache
from src.llm.providers.gpt import OpenAIProvider
import os
from dotenv import load_dotenv
load_dotenv()

HTML_NEWSLETTER_THRESHOLD = 5000
PLAIN_TRANSACTIONAL_THRESHOLD = 300
INTENTS = ["newsletter","notification","transactional","personal"]

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR/"data"/"cache_data"/"llm_cache.db"
MODEL_NAME = "gpt-oss-120b"
POSTGRES_DBI_URI = "postgresql://mailmind_admin:MT10-142020@localhost:5432/mailmind_db"
NAMESPACE_WATCHES = ("mailmind", "deferred_watches")

embedding_model = HuggingFaceEmbeddings(model="BAAI/bge-base-en-v1.5",encode_kwargs={"normalize_embeddings":True})
cache = SQLiteLLMCache(db_path=DB_PATH)
llm = ChatOpenAI(base_url="https://openrouter.ai/api/v1",model="openai/gpt-oss-120b",api_key=os.getenv("OPENROUTER_API_KEY"))
provider = OpenAIProvider()