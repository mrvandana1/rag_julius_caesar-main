import json
import requests
from tqdm import tqdm

BACKEND_URL = "http://localhost:8000/query"  
INPUT_QUESTIONS = "questions.json"
OUTPUT_DATASET = "rag_dataset.json"


def build_rag_dataset():
    
    with open(INPUT_QUESTIONS, "r", encoding="utf-8") as f:
        questions = json.load(f)

    output_rows = []

    print("\nGenerating dataset from backend...\n")

    for item in tqdm(questions):
        q = item["question"]
        gt = item["ideal_answer"]

        try:
           
            res = requests.post(
                BACKEND_URL,
                json={"query": q},
                timeout=40
            ).json()

            answer = res.get("answer", "")
            sources = res.get("sources", [])

           
            contexts = [s.get("text", "") for s in sources]

        except Exception as e:
            answer = f"ERROR: {e}"
            contexts = []

       
        output_rows.append({
            "question": q,
            "contexts": contexts,
            "ground_truth": gt,
            "answer": answer
        })

   
    with open(OUTPUT_DATASET, "w", encoding="utf-8") as f:
        json.dump(output_rows, f, indent=2, ensure_ascii=False)

    print(f"\nDataset created successfully → {OUTPUT_DATASET}\n")


if __name__ == "__main__":
    build_rag_dataset()

