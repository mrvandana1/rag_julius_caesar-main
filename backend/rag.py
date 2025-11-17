from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import chromadb
import numpy as np
import os

# --------------------------------------------------------
# Load environment
# --------------------------------------------------------
load_dotenv("../.env")

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Please set GEMINI_API_KEY in your .env file")

GENIE_MODEL = "gemini-2.0-flash"
TOP_K = 2

CHROMA_PATH = "../chroma_julius_caesar"

# --------------------------------------------------------
# Load Chroma Collections 
# --------------------------------------------------------
client = chromadb.PersistentClient(path=CHROMA_PATH)

collections = {
    "scene":        client.get_collection("julius_caesar_scene"),
    "explanation":  client.get_collection("julius_caesar_explanation"),   # NEW
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

embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")


# --------------------------------------------------------
# Vector utility
# --------------------------------------------------------
def normalize(v):
    v = np.array(v)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


# --------------------------------------------------------
# RETRIEVER with weighting and ordered priority
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
                "confidence": float(final_conf)
            })

    # sort by weighted confidence
    results = sorted(results, key=lambda x: x["confidence"], reverse=True)
    return results


# --------------------------------------------------------
# Build Context 
# --------------------------------------------------------
def build_context_text(chunks):
    ctx = []
    for c in chunks:
        m = c["metadata"]
        act = m.get("act")
        scene = m.get("scene")
        speaker = m.get("speaker", "unknown")
        ctx.append(f"[Act {act}] [Scene {scene}] [Speaker: {speaker}] {c['chunk']}")
    return "\n\n".join(ctx)


# --------------------------------------------------------
# Prompt 
# --------------------------------------------------------
def build_system_prompt():
    return (
        "Use only the information found in the retrieved context.\n"
        "Do not add external knowledge or guess beyond the text.\n"
        "Cite Act and Scene for every supported claim.\n"
        "Maintain scholarly, analytical tone suitable for literature study.\n"
        "If the context is weak, rely strictly on whatever clues are present without inventing details."
    )





# --------------------------------------------------------
# LLM
# --------------------------------------------------------
llm = ChatGoogleGenerativeAI(
    model=GENIE_MODEL,
    google_api_key=API_KEY,
)


# --------------------------------------------------------
# Generator
# --------------------------------------------------------
def generate_answer(query, chunks):
    system_prompt = build_system_prompt()
    context_text = build_context_text(chunks)

    prompt = (
        f"{system_prompt}\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {query}\n\n"
        "Answer concisely with Act and Scene references."
    )

    message = HumanMessage(content=prompt)
    response = llm.invoke([message])
    return response.content if hasattr(response, "content") else str(response)


# --------------------------------------------------------
# FULL RAG PIPELINE
# --------------------------------------------------------
def rag_pipeline(query):
    chunks = retrieve_top_k(query)
    answer = generate_answer(query, chunks)
    return answer, chunks
