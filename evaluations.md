EVALUATION.md
Retrieval-Augmented Generation (RAG) System Evaluation Report
1. Introduction
This evaluation examines the performance of our Shakespeare "Julius Caesar" RAG system using a structured testbed of 35+(25 given and 10 curated) questions, covering:
We used RAGAS as our evaluation framework, scoring:
Answer Relevancy – Does the model answer the question meaningfully?
Faithfulness – Does the answer stay anchored to retrieved context?
Context Precision – Did the retriever fetch the correct evidence?

2. Evaluation Methodology
2.1 Dataset Construction (Testbed)
The testbed contains 35+ question divided into:
Given questions (1–25)
created questions (26–35)
More challenging and higher-order, including:
Multi-scene comparison
Theme-based questions
Motivation analysis
This mix allows us to stress-test both retrieval grounding and LLM reasoning.
Complete Question List in (testbed json file)
This testbed is balanced, comprehensive.


3. Quantitative Evaluation (RAGAS)
We evaluated all 35+ samples using:
Answer Relevancy
Faithfulness
Context Precision
The results :
3.1 General Trends
Answer Relevancy: 0.70–0.95 (strong)
The LLM usually understands the question. Even when context is missing, relevancy stays high, meaning the LLM is strong at comprehension.
Faithfulness: 0.0 – 1.0 (high variance)
Many answers score 1.0 → the LLM follows the rule “use only retrieved context.”
But some scores 0.0–0.5, indicating the LLM:filled gaps with hallucinations relied on prior training when context was missing
Context Precision: 0.0 – 1.0 (most critical issue)
This is where the system struggled the most.
Literal questions → CP = 0.9–1.0
Multi-scene or thematic → CP = 0.0–0.4
Low CP means:
The retriever did not fetch the correct scene(s) for the question.
This caused nearly all hallucinations and incorrect answers.

4. Qualitative Analysis
Below is the deep-dive reasons behind failures and successes.
4.1 Where the System Succeeded
A. Scene-specific, literal, keyword-based questions
Examples:
“What does the Soothsayer say to Caesar?” (CP  0.95)
“What happens to Cinna the poet?” (CP 0.88)
“What does Antony do when he arrives at Caesar’s body?” (CP ≈ 1.0)
These succeeded because:
The questions contain explicit scene identifiers.
Keywords match directly with the chunk text
The relevant lines exist in a single scene → short retrieval distance.
Gemini Flash + RAGAS wrapper stays faithful when given clean context.

Conclusion:
retriever works best when evidence is short, literal, uniquely located, and keyword identifiable.

4.2 Where the System Failed
A. Multi-scene reasoning
Failures on:
Funeral speech comparison
Miscommunication in the tragedy
Themes of public vs private self
These questions require:
Combining Acts
Recognizing character arcs
Summarizing multiple scenes

retriever only returns 1–2 chunks, so the LLM lacks full evidence.
B. Questions where the answer doesn’t appear verbatim
Example:
“What news do Brutus and Cassius receive from Rome?”
Context Precision = 0.0
The retriever pulled Act 3 content instead of Act 4.
Reason:
Query doesn’t contain exact keywords (“Portia,” “senators,” etc.)
Thematically distant from retrieved chunks

C. Questions involving metaphor or interpretation

Example:
“What is the significance of the contrast between Brutus’s and Antony’s speeches?”
The answer requires:
Understanding rhetoric
Structure of prose vs verse

No chunk provides all these directly.


D. Questions dependent on character motivation
“In what way does Caesar demonstrate public vs private self?”
Requires:
Act 1 context (Cassius story)
Act 2 context (superstition)
Act 3 context (Northern Star speech)
Single chunk won’t contain it.
retriever fails → LLM guesses.

4.3 Why These Failures Occur
1. Small chunk size
Chunks are too granular → single-scene answers are okay, but cross-scene logic fails.
2. Single-query retrieval
Only the raw question is embedded → thematic questions are under-represented in vector space.
(can use  llm to generate versions of the question)
3. Further RAG techniques
Query expansion
Multi-vector retriever

4. Strengths of the System

Gemini Flash provides high-quality, relevant responses.
Good performance on short, direct recall

High precision for questions rooted in a single scene.
Mostly faithful answers when context is relevant

LLM obeys the RAG constraints.

5. Weaknesses of the System
Retrieval bottleneck (biggest weakness)
Almost all low-faithfulness answers occurred when context precision < 0.5.
Lack of multi-scene retrieval capabilities
