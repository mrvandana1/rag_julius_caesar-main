# ===============================================================
# Create Context-Window Chunks from Speaker-Level Julius Caesar Data
# (VS Code version)
# ===============================================================

import json

# ---------- Local Paths ----------
INPUT_PATH = "./julius_caesar_chunks.jsonl"
OUTPUT_PATH = "./julius_caesar_context_windows.jsonl"

WINDOW_SIZE = 5    # number of chunks in each window
STEP_SIZE = 3      # overlap between windows


# ---------- Load Speaker-Level Chunks ----------
def load_chunks(path):
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line.strip()))
    return chunks


# ---------- Create Overlapping Windows ----------
def merge_window(chunks):
    merged = []
    win_id = 0
    n = len(chunks)

    for i in range(0, n, STEP_SIZE):
        window = chunks[i:i + WINDOW_SIZE]

        if not window:
            continue

        # Act/Scene from first chunk
        act = window[0].get("act")
        scene = window[0].get("scene")

        combined_text_parts = []
        for c in window:
            speaker = c.get("speaker")
            text = c.get("text", "").strip()

            if speaker:
                combined_text_parts.append(f"{speaker}: {text}")
            else:
                combined_text_parts.append(text)

        combined_text = " ".join(combined_text_parts).strip()
        word_count = len(combined_text.split())

        merged.append({
            "window_id": win_id,
            "act": act,
            "scene": scene,
            "type": "context_window",
            "text": combined_text,
            "textLength": len(combined_text),
            "wordCount": word_count
        })

        win_id += 1

    return merged


# ---------- Run ----------
print("📘 Loading speaker-level chunks...")
chunks = load_chunks(INPUT_PATH)
print(f"Loaded {len(chunks)} speaker chunks.")

print("🧩 Creating context windows...")
windows = merge_window(chunks)

# ---------- Save ----------
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for w in windows:
        f.write(json.dumps(w, ensure_ascii=False) + "\n")

print(f"\n✅ Created {len(windows)} context-window chunks.")
print(f"📁 Saved to: {OUTPUT_PATH}")

# ---------- Print Examples ----------
print("\n🔹Example windows:")
for w in windows[:3]:
    print({
        "window_id": w["window_id"],
        "act": w["act"],
        "scene": w["scene"],
        "wordCount": w["wordCount"],
        "text_preview": w["text"][:180] + ("..." if len(w["text"]) > 180 else "")
    })
