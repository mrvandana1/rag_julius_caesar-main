import json
import pandas as pd
import matplotlib.pyplot as plt

# ----------------------------------------------------
# Load your RAGAS JSONL file
# ----------------------------------------------------
FILE_PATH = "ragas_stepwise (1).jsonl"

records = []
with open(FILE_PATH, "r", encoding="utf-8") as f:
    for line in f:
        try:
            records.append(json.loads(line))
        except:
            pass  # skip malformed lines

df = pd.DataFrame(records)

print("Loaded rows:", len(df))
print(df.head())

# ----------------------------------------------------
# 1. Histogram: Faithfulness
# ----------------------------------------------------
plt.figure()
plt.hist(df["faithfulness"])
plt.xlabel("Faithfulness")
plt.ylabel("Count")
plt.title("Distribution of Faithfulness Scores")
plt.show()

# ----------------------------------------------------
# 2. Histogram: Context Precision
# ----------------------------------------------------
plt.figure()
plt.hist(df["context_precision"])
plt.xlabel("Context Precision")
plt.ylabel("Count")
plt.title("Distribution of Context Precision Scores")
plt.show()

# ----------------------------------------------------
# 3. Histogram: Answer Relevancy
# ----------------------------------------------------
plt.figure()
plt.hist(df["answer_relevancy"])
plt.xlabel("Answer Relevancy")
plt.ylabel("Count")
plt.title("Distribution of Answer Relevancy Scores")
plt.show()

# ----------------------------------------------------
# 4. Scatter: Faithfulness vs Context Precision
# ----------------------------------------------------
plt.figure()
plt.scatter(df["faithfulness"], df["context_precision"])
plt.xlabel("Faithfulness")
plt.ylabel("Context Precision")
plt.title("Faithfulness vs Context Precision")
plt.show()

# ----------------------------------------------------
# 5. Scatter: Answer Relevancy vs Faithfulness
# ----------------------------------------------------
plt.figure()
plt.scatter(df["answer_relevancy"], df["faithfulness"])
plt.xlabel("Answer Relevancy")
plt.ylabel("Faithfulness")
plt.title("Answer Relevancy vs Faithfulness")
plt.show()

# ----------------------------------------------------
# 6. Scatter: Answer Relevancy vs Context Precision
# ----------------------------------------------------
plt.figure()
plt.scatter(df["answer_relevancy"], df["context_precision"])
plt.xlabel("Answer Relevancy")
plt.ylabel("Context Precision")
plt.title("Answer Relevancy vs Context Precision")
plt.show()

# ----------------------------------------------------
# 7. Optional: Print summary statistics
# ----------------------------------------------------
print("\n=== SUMMARY STATISTICS ===")
print(df[["answer_relevancy", "faithfulness", "context_precision"]].describe())
