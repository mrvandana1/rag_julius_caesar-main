# Julius Caesar RAG Expert System

## 1. Project Overview

This project implements a **Retrieval-Augmented Generation (RAG)** expert system for *Shakespeare’s Julius Caesar*.  
It enables users to ask natural-language questions about the play and receive:

- **Scholarly, citation-rich answers**
- **Act/Scene–grounded evidence**
- **Transparent retrieved chunks**
- **Confidence-weighted retrieval explanations**

### 🔧 End-to-End System Components

- PDF ingestion & structured chunking of *Julius Caesar*
- **Multi-level semantic chunking**:
  - Speaker-level
  - Context-window
  - Scene-level
  - Explanation-level (manual summaries)
- Dense embeddings stored in **ChromaDB** (persistent)
- **Weighted retrieval** across four semantic granularities
- **Gemini 2.0 Flash** for generation
- **FastAPI backend + Streamlit frontend**
  - Users interact via Streamlit
  - Streamlit → FastAPI → RAG pipeline → Answer + Evidence

## Folder Structure
``` 
backend/
│
├── Dockerfile # Backend Docker config
├── main.py # FastAPI backend entrypoint
├── rag.py # Core RAG pipeline
├── requirements.txt # Backend dependencies
│
├── chroma_julius_caesar/ # Persistent ChromaDB (vector store)
│ └── chroma.sqlite3 # Chroma database file 
│
├── chunking/ # Chunk-generation scripts
│ ├── context_window.py
│ ├── scene_level.py
│ ├── scene_level_summarised.py
│ └── speaker_level.py
│
├── indexing/ # Index-building scripts
│ └── generate_chromadb.py
│
├── chunks/ # Pre-generated chunk JSONL files
│ ├── julius_caesar_chunks.jsonl
│ ├── julius_caesar_context_windows.jsonl
│ ├── julius_caesar_explanation_chunks.jsonl
│ └── julius_caesar_scene_chunks.jsonl
│
├── evaluation/ # RAG evaluation utilities
│ ├── evaluate.py
│ ├── questions.json
│ └── rag_dataset.json
│
frontend/
│
├── Dockerfile # Frontend Docker config
└── frontend.py # Streamlit UI
```
---

## 2. System Architecture
<img width="570" height="813" alt="Screenshot from 2025-11-16 22-34-47" src="https://github.com/user-attachments/assets/1ae4eb14-5cd0-4a70-98cc-8d298e30069c" />


---

## 3. Design Choices

## ✅ Design Justification

This RAG system uses **four granularities of chunking**, each solving a different retrieval failure mode in Shakespearean text.

---

### ### **A. Speaker-Level Chunks**

**Purpose**
- Capture individual speeches and who says what
- Useful for questions about motives, personality, conflict

**Why Needed**
- Shakespeare’s meaning often lies in single lines
- Enables pinpoint retrieval  
  *Example:* “What does Cassius say about fate?”

---

### ### **B. Context-Window Chunks**

**Purpose**
- Capture dialogue flow using sliding windows of 3–5 speeches

**Why Needed**
- Pure speaker chunks break continuity
- Restores local narrative context
- Helps with interpretation where meaning spans multiple lines

---

### ### **C. Scene-Level Chunks**

**Purpose**
- Capture global thematic, emotional, and narrative meaning

**Why Needed**
- Many questions require entire-scene context:
  - Character motivations  
  - Emotional build-ups  
  - Causal relationships  
- Crucial for interpretive literature analysis

---

### ### **D. Explanation-Level Chunks (Manual Summaries)**

**Purpose**
- Provide human-level, concise summaries of scenes/acts  
- Help answer high-level conceptual or thematic questions

**Why Needed**
- LLMs perform best with a “middle abstraction layer”
- Enables complex reasoning such as:
  *“Compare Caesar’s ambition with Brutus’s values.”*

---

## ⭐ Why Four Levels?

Each chunk type has strengths and weaknesses:

| Chunk Type      | Strength                  | Weakness                         |
|-----------------|---------------------------|----------------------------------|
| Speaker         | High precision            | No broader context               |
| Window          | Restores dialogue flow    | Still narrow for thematic analysis |
| Scene           | Rich global meaning       | Long for some questions          |
| Explanation     | Strong conceptual clarity | Loses exact text fidelity        |

**Combining all four produces the strongest hybrid retrieval system.**

---

## Embedding Model Choice: **BGE Base (bge-base-en-v1.5)**

### ✔ Why BGE?

- State-of-the-art dense retrieval performance  
- Strong for abstract + literary semantic similarity  
- Outperforms MiniLM, MPNet, GloVe on long textual sequences  
- Free, open-source, reproducible  
- Excellent for Shakespeare’s long, structured lines

### ✔ Why not OpenAI/Gemini embeddings?

- Costly  
- Not offline-friendly  
- Harder to reproduce  
- BGE gives consistent, high-quality performance locally

---

## LLM Choice: **Gemini 2.0 Flash**

### ✔ Why Gemini 2.0 Flash?

- Extremely fast (ideal for interactive systems)
- Strong reasoning on literature content
- Great contextual grounding
- Low-latency generation
- Handles multi-paragraph answers + citations effectively

---

## ✔ System Prompt Enforcement

The LLM is strictly constrained to:

- Use **only retrieved context**
- Avoid hallucinations
- Cite **Act/Scene consistently**
- Maintain a scholarly tone

This ensures answers match academic expectations.

---
## Instructions: Run Project Using Docker Compose

### 1. Requirements
Install:
- Docker
- Docker Compose

### 2. Project Structure
Ensure a `.env` file exists with:
GEMINI_API_KEY=your_api_key_here

### 3. Build the Docker Images
docker compose build

### 4. Start the System
docker compose up

### 5. Access the Application
- Frontend (Streamlit): http://localhost:8501  
- Backend (FastAPI): http://localhost:8000  
- API Docs: http://localhost:8000/docs  

### 6. Stop the Containers

 - docker compose down

---
## Contribution 

## 1.Saketh-Chunk Strategies, ChromaDB Indexing, Web UI Interface
- Chunking Strategies  
- ChromaDB Indexing
- Retriever 
- Backend

## 2.Mohan- RAGs Evaluation, Retriever, Docker, EVAL.md
- RAGs Evaluation  
- Retriever  
- Docker  
- EVAL.md  

## 3.Vikash- Test Bed Questions, EVAL.md, Docker
- Test Bed Questions  
- EVAL.md  
- Docker
- Prompting Technique

