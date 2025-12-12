import chromadb
import numpy as np
from sentence_transformers import SentenceTransformer

# --------------------------------------------------------
# TEST MODE (LLM is disabled) ok
# --------------------------------------------------------
TEST_MODE = True

TOP_K = 2

# Path to chroma folder INSIDE backend/
CHROMA_PATH = "./chroma_julius_caesar"

# --------------------------------------------------------
# Load Chroma Persistent Client
# --------------------------------------------------------
client = chromadb.PersistentClient(path=CHROMA_PATH)

collections = {
    "scene":        client.get_collection("julius_caesar_scene"),
    "explanation":  client.get_collection("julius_caesar_explanation"),
    "context":      client.get_collection("julius_caesar_context"),
    "speaker":      client.get_collection("julius_caesar_speaker")
}

# Retrieval weights for ranking
COLLECTION_WEIGHTS = {
    "scene":        1.40,
    "explanation":  1.30,
    "context":      1.10,
    "speaker":      1.00
}

# Embedding model
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")

# --------------------------------------------------------
# Vector normalization
# --------------------------------------------------------
def normalize(v):
    v = np.array(v)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v

# --------------------------------------------------------
# RETRIEVAL: Weighted ranking across collections
# --------------------------------------------------------
def retrieve_top_k(query, k=TOP_K):
    q_vec = normalize(embedder.encode(query)).tolist()
    results = []

    for name in ["scene", "explanation", "context", "speaker"]:
        coll = collections[name]
        res = coll.query(query_embeddings=[q_vec], n_results=k)

        docs = res["documents"][0]
        metas = res["metadatas"][0]
        distances = res["distances"][0]
        weight = COLLECTION_WEIGHTS[name]

        for doc, meta, dist in zip(docs, metas, distances):
            base_conf = 1 / (1 + dist)
            final_conf = base_conf * weight

            results.append({
                "collection": name,
                "chunk": doc,
                "metadata": meta,
                "confidence": float(final_conf),
            })

    results = sorted(results, key=lambda x: x["confidence"], reverse=True)
    return results

# --------------------------------------------------------
# TEST-MODE Answer Generator (NO LLM)
# --------------------------------------------------------
def generate_answer(query, chunks):
    if chunks:
        top = chunks[0]["chunk"]
        return f"Context-based summary (test mode): {top[:250]}..."
    else:
        return "No relevant context found (test mode)."

# --------------------------------------------------------
# FULL RAG PIPELINE
# --------------------------------------------------------
def rag_pipeline(query):
    chunks = retrieve_top_k(query)
    answer = generate_answer(query, chunks)
    return answer, chunks

# print(rag_pipeline("What are the main themes in Julius Caesar?"))