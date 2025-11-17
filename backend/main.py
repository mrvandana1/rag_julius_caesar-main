from fastapi import FastAPI
from pydantic import BaseModel
from rag import rag_pipeline

app = FastAPI(
    title="Shakespearean Scholar RAG API",
    description="Backend API for Julius Caesar Expert System",
    version="1.0",
)

class Query(BaseModel):
    query: str

@app.post("/query")
def ask_question(body: Query):
    answer, raw_sources = rag_pipeline(body.query)

    cleaned_sources = []
    for s in raw_sources:
        md = s["metadata"]

        cleaned_sources.append({
            "text": s["chunk"],
            "act": md.get("act"),
            "scene": md.get("scene"),
            "collection": s["collection"],
            "confidence": round(s["confidence"], 4)
        })

    
    cleaned_sources = sorted(cleaned_sources, key=lambda x: x["confidence"], reverse=True)

    return {
        "answer": answer,
        "sources": cleaned_sources
    }
