import json
from collections import defaultdict

# ---------- Local Paths ----------
INPUT_PATH = "./julius_caesar_chunks.jsonl"
OUTPUT_PATH = "./julius_caesar_scene_chunks.jsonl"


# ---------- Load Speaker-Level Chunks ----------
def load_chunks(path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


# ---------- Make Scene-Level Merged Chunks ----------
def make_scene_chunks(chunks):
    scene_dict = defaultdict(list)

    # Group all text lines by (act, scene)
    for ch in chunks:
        act = ch.get("act")
        scene = ch.get("scene")
        key = (act, scene)

        if ch.get("text"):
            scene_dict[key].append(ch["text"].strip())

    # Create merged scene chunks
    scene_chunks = []
    scene_id = 0

    for (act, scene), texts in scene_dict.items():
        combined_text = " ".join(texts)

        scene_chunks.append({
            "id": scene_id,
            "act": act,
            "scene": scene,
            "speaker": None,              # always None for scene-level
            "type": "scene_context",
            "text": combined_text.strip()
        })

        scene_id += 1

    return scene_chunks


# ---------- Run ----------
chunks = load_chunks(INPUT_PATH)

scene_chunks = make_scene_chunks(chunks)

# ---------- Save ----------
with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    for sc in scene_chunks:
        f.write(json.dumps(sc, ensure_ascii=False) + "\n")

print(f"✅ Created {len(scene_chunks)} scene-level chunks")
print(f"📁 Saved to: {OUTPUT_PATH}")

print("\n🔹Example:")
for s in scene_chunks[:3]:
    print(s)
