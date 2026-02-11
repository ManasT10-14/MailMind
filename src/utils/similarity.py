from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np
embedding_model = HuggingFaceEmbeddings(model="BAAI/bge-base-en-v1.5",encode_kwargs={"normalize_embeddings":True})
def top_k_similar_texts(query, text_embeddings,watches, embedder = embedding_model, k=3):
    query_embedding = embedder.embed_query(query)
    scores = np.dot(text_embeddings, query_embedding)
    top_indices = np.argsort(scores)[-k:][::-1]
    return [(watches[i], scores[i]) for i in top_indices]
