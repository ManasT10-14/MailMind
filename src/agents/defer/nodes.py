from src.llm.service import call_llm_cached
from src.schema.email_object import EmailObject
from src.schema.check_watch_state_schema import CheckStateSchema
from src.schema.deferred_watch_schema import DeferredWatchSchema
from src.schema.router_schema import RouterSchema
from typing import List,TypedDict,Dict,Literal,Any,Annotated
from operator import or_
from langgraph.graph import StateGraph,START,END
from langgraph.types import Command,Send
from src.config import MODEL_NAME
from src.agents.defer.state import DeferState
from langgraph.store.postgres import PostgresStore
from src.prompts.create_watch_prompt import SYSTEM_PROMPT_CREATE_WATCH,PROMPT_VERSION_CREATE_WATCH,build_create_watch_prompt
from uuid import uuid4
from src.config import POSTGRES_DBI_URI,NAMESPACE_WATCHES
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from src.utils.similarity import top_k_similar_texts
from src.prompts.check_watch_state_prompt import PROMPT_VERSION_CHECK_STATE,SYSTEM_PROMPT_CHECK_STATE,build_check_state_prompt
from src.agents.router.graph import build_graph
from src.agents.router.init_state_builder import build_initial_state
# embedding_model = HuggingFaceEmbeddings(model="BAAI/bge-base-en-v1.5",encode_kwargs={"normalize_embeddings":True})
def router(state: DeferState) -> Command[Literal["create_watch","filter_watches"]]:
    action:RouterSchema = state["email_action_details"]
    if action.action == "DEFER":
        return Command(goto="create_watch")
    return Command(goto="filter_watches")

def create_watch(state: DeferState)-> Command[Literal[END]]:
    email: EmailObject = state["email"]
    summarizer_prompt = build_create_watch_prompt(email=email)
    result: DeferredWatchSchema = call_llm_cached(cache=state["cache"],llm=state["llm"],provider=state["provider"],model_name=MODEL_NAME,system_prompt=SYSTEM_PROMPT_CREATE_WATCH,user_prompt=summarizer_prompt,output_schema=DeferredWatchSchema,prompt_version=PROMPT_VERSION_CREATE_WATCH,agent_name="DeferredAgent",cache_enabled=True)
    
    embedding_model = state["embedding_model"]
    to_embed = f"{result['watch_summary']}. Waiting for: {result['waiting_for']}"
    result["watch_id"] = str(uuid4())
    result["source_email_id"] = email.message_id
    result["sender"] = email.metadata.sender
    result["status"] = "active"
    result["embedding"] = embedding_model.embed_query(to_embed)
    with PostgresStore.from_conn_string(POSTGRES_DBI_URI) as store:  
        store.put(
        namespace=NAMESPACE_WATCHES,
        key=result["watch_id"],
        value=result
    )
    return Command(goto=END,update={"run_router":False})

def filter_watches(state:DeferState) -> Command[Literal["check_state"]]:
    email:EmailObject = state["email"]
    router_schema: RouterSchema = state["email_action_details"]
    email_summary = router_schema.email_summary
    sender = email.metadata.sender
    with PostgresStore.from_conn_string(POSTGRES_DBI_URI) as store: 
        watches = store.search(NAMESPACE_WATCHES)
        
    active_watches = []
    for watch in watches:
        if watch.value["status"] == "active":
            active_watches.append(watch)
            
    if len(active_watches) == 0:
        return Command(goto=END, update={"relevant_watches": []})

    
    relevant_watches = []
    watches_embedded = [watch.value["embedding"] for watch in active_watches]
    for watch in active_watches:
        if watch.value["sender"] == sender:
            relevant_watches.append(watch)
    
    if len(relevant_watches) == 0:
        relevant_watches = top_k_similar_texts(email_summary,watches_embedded,active_watches)
        relevant_watches = [watch for watch,_ in relevant_watches]
    
    
    if len(relevant_watches) >5:
        watches_embedded = [watch.value["embedding"] for watch in relevant_watches]
        relevant_watches = top_k_similar_texts(email_summary,watches_embedded,relevant_watches)
        relevant_watches = [watch for watch,_ in relevant_watches]
    

    return Command(goto="check_state",update={"relevant_watches":relevant_watches})

def check_state(state: DeferState):
    relevant_watches = [watch.value for watch in state["relevant_watches"]]
    prompt  = build_check_state_prompt(email=state["email"],watches=relevant_watches)
    result:CheckStateSchema = call_llm_cached(cache=state["cache"],llm=state["llm"],provider=state["provider"],model_name=MODEL_NAME,system_prompt=SYSTEM_PROMPT_CHECK_STATE,user_prompt=prompt,output_schema=CheckStateSchema,prompt_version=PROMPT_VERSION_CHECK_STATE,agent_name="DeferredAgent",cache_enabled=True)

    watches_decision = result.watch_decisions
    with PostgresStore.from_conn_string(POSTGRES_DBI_URI) as store:
        for watch_decision in watches_decision:
            if watch_decision.decision != "NO_CHANGE":
                    watch = store.get(NAMESPACE_WATCHES,key=watch_decision.watch_id)
                    if watch_decision.updated_watch:
                        watch.value["watch_summary"] = watch_decision.updated_watch.watch_summary
                        watch.value["waiting_for"] = watch_decision.updated_watch.waiting_for 
                        to_embed = f"{watch.value['watch_summary']}. Waiting for: {watch.value['waiting_for']}"
                        embedding_model = state["embedding_model"]
                        watch.value["embedding"] = embedding_model.embed_query(to_embed)
                    if watch_decision.decision == "UPDATE":
                        watch.value["status"] = "active"
                    elif watch_decision.decision == "RESOLVED":
                        watch.value["status"] = "resolved"
                    elif watch_decision.decision == "ESCALATED":
                        watch.value["status"] = "escalated"
                    store.put(NAMESPACE_WATCHES,key=watch_decision.watch_id,value = watch.value)

    # if result.context_summary:
    #     return Command(goto="call_router")
    return Command(goto=END,update={"router_summary":result.context_summary,"run_router":True})
