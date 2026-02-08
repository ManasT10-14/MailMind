from pathlib import Path

HTML_NEWSLETTER_THRESHOLD = 5000
PLAIN_TRANSACTIONAL_THRESHOLD = 300
INTENTS = ["newsletter","notification","transactional","personal"]

BASE_DIR = Path(__file__).resolve().parents[1]
DB_PATH = BASE_DIR/"data"/"cache_data"/"llm_cache.db"
MODEL_NAME = "gpt-oss-120b"

print(DB_PATH)