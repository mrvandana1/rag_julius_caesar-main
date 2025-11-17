import json
import os
import chromadb
from sentence_transformers import SentenceTransformer

# -------------------------
# FILE PATHS
# -------------------------
SPEAKER_PATH = "./julius_caesar_chunks.jsonl"
CONTEXT_PATH = "./julius_caesar_context_windows.jsonl"
SCENE_PATH   = "./julius_caesar_scene_chunks.jsonl"
EXPLAIN_PATH = "./julius_caesar_explanation_chunks.jsonl"   # NEW

# Where Chroma will be saved (persistent)
CHROMA_PATH = "./chroma_julius_caesar"


# -------------------------
# LOAD CHUNKS
# -------------------------
def load_chunks(path):
    data = []
    if not os.path.exists(path):
        print(f"⚠️ File not found: {path}")
        return []

    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            data.append(json.loads(line.strip()))
    return data


speaker_chunks   = load_chunks(SPEAKER_PATH)
context_chunks   = load_chunks(CONTEXT_PATH)
scene_chunks     = load_chunks(SCENE_PATH)
explain_chunks   = load_chunks(EXPLAIN_PATH)   # NEW

print(f"Speaker chunks: {len(speaker_chunks)}")
print(f"Context-window chunks: {len(context_chunks)}")
print(f"Scene chunks: {len(scene_chunks)}")
print(f"Explanation chunks: {len(explain_chunks)}")


# -------------------------
# EMBEDDING MODEL
# -------------------------
print("\n🔹 Loading embedding model (bge-base-en-v1.5)...")
embedder = SentenceTransformer("BAAI/bge-base-en-v1.5")
print("✅ Embedding model loaded.\n")


# -------------------------
# INITIALIZE CHROMA (PERSISTENT)
# -------------------------
print(f"📦 Initializing Chroma at: {CHROMA_PATH}")
client = chromadb.PersistentClient(path=CHROMA_PATH)

collections = {
    "speaker":     client.get_or_create_collection("julius_caesar_speaker"),
    "context":     client.get_or_create_collection("julius_caesar_context"),
    "scene":       client.get_or_create_collection("julius_caesar_scene"),
    "explanation": client.get_or_create_collection("julius_caesar_explanation")  # NEW
}


# -------------------------
# ADD TO COLLECTION
# -------------------------
def add_to_collection(collection, chunks):
    docs = []
    metas = []
    ids = []

    for c in chunks:
        if not c.get("text"):
            continue

        docs.append(c["text"])
        metas.append({
            "act": c.get("act"),
            "scene": c.get("scene"),
            "type": c.get("type")
        })
        ids.append(str(c["id"]))

    if not docs:
        print(f"⚠️ No docs for collection: {collection.name}")
        return

    print(f"🔹 Embedding {len(docs)} items for '{collection.name}'...")
    vectors = embedder.encode(docs, normalize_embeddings=True).tolist()

    collection.add(
        documents=docs,
        embeddings=vectors,
        metadatas=metas,
        ids=ids
    )

    print(f"✅ Done: {collection.name}\n")


# -------------------------
# ADD ALL CHUNK TYPES
# -------------------------
add_to_collection(collections["speaker"], speaker_chunks)
add_to_collection(collections["context"], context_chunks)
add_to_collection(collections["scene"], scene_chunks)
add_to_collection(collections["explanation"], explain_chunks)   # NEW

print("\n🎉 All Chroma collections updated successfully!")
print(f"📁 Stored at: {CHROMA_PATH}")
