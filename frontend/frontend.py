import streamlit as st
import requests

st.set_page_config(page_title="Shakespearean Scholar", layout="wide")

st.title(" broom Shakespearean Scholar – Julius Caesar RAG System")
st.write("Ask me bro any question about *Julius Caesar* and get a scholarly answer with citations.")
##
# API_URL = "http://localhost:8000/query"
import os
API_URL = os.getenv("BACKEND_URL", "http://localhost:8000/query")

def conf_color(conf):
    if conf >= 0.75: return "🟢"
    if conf >= 0.45: return "🟡"
    return "🔴"

query = st.text_input("Enter your question:")

if st.button("Ask"):
    if not query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking like a Shakespearean Scholar..."):
            try:
                response = requests.post(API_URL, json={"query": query})
                data = response.json()

                st.subheader("📘 Answer")
                st.write(data["answer"])

                st.subheader("📚 Supporting Sources")

                
                sources = sorted(data["sources"], key=lambda x: x["confidence"], reverse=True)

                for i, src in enumerate(sources, start=1):
                    color = conf_color(src["confidence"])
                    title = (
                        f"{color} Source {i} | "
                        f"Act {src['act']} Scene {src['scene']} | "
                        f"{src['collection']} | "
                        f"Confidence: {src['confidence']}"
                    )

                    with st.expander(title):
                        st.write(src["text"])

            except Exception as e:
                st.error(f"Error: {e}")
