from langgraph.store.postgres import PostgresStore
from src.config import POSTGRES_DBI_URI
with PostgresStore.from_conn_string(POSTGRES_DBI_URI) as store:
    store.setup()

