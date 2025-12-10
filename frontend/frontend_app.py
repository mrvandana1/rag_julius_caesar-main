import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:8000/compute")

st.title("Scientific Calculator (Microservice Version)")

operation = st.selectbox("Choose operation:", ["sqrt", "factorial", "ln", "power"])

payload = {"operation": operation}

if operation in ["sqrt", "ln"]:
    x = st.number_input("Enter x:")
    payload["x"] = x

elif operation == "factorial":
    n = st.number_input("Enter n:", min_value=0, step=1)
    payload["n"] = n

elif operation == "power":
    x = st.number_input("Enter x:")
    b = st.number_input("Enter exponent (b):")
    payload["x"] = x
    payload["b"] = b

if st.button("Compute"):
    response = requests.post(BACKEND_URL, json=payload)
    if response.status_code == 200:
        st.success(f"Result = {response.json()['result']}")
    else:
        st.error(response.json().get("error"))
