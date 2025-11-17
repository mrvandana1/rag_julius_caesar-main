import json
from collections import defaultdict
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    google_api_key=API_KEY,
    temperature=0
)


INPUT_PATH = "julius_caesar_chunks.jsonl"


OUTPUT_PATH = "julius_caesar_explanation_chunks.jsonl"


# ------------------------------------------
# Load all speaker-level chunks
# ------------------------------------------
def load_speaker_chunks(path):
    chunks = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            chunks.append(json.loads(line.strip()))
    return chunks


# ------------------------------------------
# Group chunks by (act, scene)
# ------------------------------------------
def group_by_scene(chunks):
    scene_dict = defaultdict(list)

    for ch in chunks:
        act = ch["act"]
        scene = ch["scene"]
        key = (act, scene)
        if ch.get("text"):
            scene_dict[key].append(ch["text"].strip())

    return scene_dict


# ------------------------------------------
# Ask LLM to produce explanation
# ------------------------------------------
def generate_explanation(act, scene, full_text):
    prompt = f"""
Write an analytical explanation of Act {act}, Scene {scene} from *Julius Caesar*.

Rules:
- DO NOT retell the whole scene.
- Focus ONLY on meaning: character motivation, emotional conflict, themes, political tension, and cause–effect.
- Write 3–5 sentences MAX.
- No external knowledge; use ONLY the text below.
- Tone should be scholarly and analytical.

Scene text:
\"\"\"
{full_text}
\"\"\"
"""

    out = llm.invoke(prompt)
    return out.content.strip()


# ------------------------------------------
# Build explanation-level chunks
# ------------------------------------------
def build_explanation_chunks(scene_dict):
    explanation_chunks = []

    for (act, scene), lines in scene_dict.items():
        combined_scene_text = " ".join(lines)
        explanation = generate_explanation(act, scene, combined_scene_text)

        explanation_chunks.append({
            "id": f"{act}_{scene}",
            "act": act,
            "scene": scene,
            "speaker": None,                   # always None for explanation
            "type": "explanation",
            "text": explanation
        })

        print(f"✓ Generated explanation for Act {act}, Scene {scene}")

    return explanation_chunks


# ------------------------------------------
# Save outputs
# ------------------------------------------
def save_jsonl(chunks, path):
    with open(path, "w", encoding="utf-8") as f:
        for ch in chunks:
            f.write(json.dumps(ch, ensure_ascii=False) + "\n")


# ------------------------------------------
# MAIN
# ------------------------------------------
def main():
    print("Loading speaker-level chunks...")
    speaker_chunks = load_speaker_chunks(INPUT_PATH)

    print("Grouping into scenes...")
    scene_dict = group_by_scene(speaker_chunks)

    print("Generating explanation-level chunks...")
    explanation_chunks = build_explanation_chunks(scene_dict)

    print("Saving...")
    save_jsonl(explanation_chunks, OUTPUT_PATH)

    print(f"\n Explanation chunks saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
