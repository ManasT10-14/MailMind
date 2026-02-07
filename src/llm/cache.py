import sqlite3
import hashlib
import json
from typing import Optional

LLM_CACHE_TABLE = {
    "table_name": "llm_cache",
    "columns": {
        "cache_key": "TEXT PRIMARY KEY",
        "response_json": "TEXT NOT NULL",
        "created_at": "TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
    },
}


def create_table_from_schema(conn: sqlite3.Connection, schema: dict) -> None:
    columns_sql = ", ".join(
        f"{name} {dtype}"
        for name, dtype in schema["columns"].items()
    )

    sql = f"""
    CREATE TABLE IF NOT EXISTS {schema["table_name"]} (
        {columns_sql}
    );
    """

    conn.execute(sql)
    conn.commit()



class SQLiteLLMCache:
    """
    SQLite-backed cache for LLM responses.
    Responsible for:
    - DB connection lifecycle
    - schema initialization
    - deterministic cache key generation
    - get/set operations
    """

    def __init__(self, db_path: str = "llm_cache.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_schema()


    def _init_schema(self) -> None:
        create_table_from_schema(self.conn, LLM_CACHE_TABLE)


    def make_cache_key(
        self,
        *,
        model_name: str,
        system_prompt: str,
        user_prompt: str,
        output_schema: dict,
        prompt_version: str,
        agent_name:str,
    ) -> str:
        """
        Create a deterministic, semantic cache key.
        Any change in inputs MUST invalidate the cache.
        """
        payload = {
            "model": model_name,
            "system_prompt": system_prompt,
            "user_prompt": user_prompt,
            "schema": output_schema,
            "prompt_version": prompt_version,
            "agent_name":agent_name,
        }

        raw = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, cache_key: str) -> Optional[dict]:
        """
        Fetch cached JSON response if present.
        Returns None on cache miss.
        """
        cur = self.conn.execute(
            "SELECT response_json FROM llm_cache WHERE cache_key = ?",
            (cache_key,),
        )
        row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def set(self, cache_key: str, value: dict) -> None:
        """
        Store structured JSON response in cache.
        """
        self.conn.execute(
            """
            INSERT OR REPLACE INTO llm_cache (cache_key, response_json)
            VALUES (?, ?)
            """,
            (cache_key, json.dumps(value)),
        )
        self.conn.commit()
