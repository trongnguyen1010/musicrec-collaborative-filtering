"""Streamlit demo that deliberately consumes the REST API instead of model code."""

import os

import requests
import streamlit as st

API_URL = os.getenv("MUSICREC_API_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="MusicRec", page_icon="🎵")
st.title("MusicRec demo")
user_id = st.text_input("User ID (tùy chọn)")
k = st.slider("Số gợi ý", min_value=1, max_value=20, value=10)

if st.button("Tạo gợi ý"):
    payload: dict[str, object] = {"k": k}
    if user_id:
        payload["user_id"] = user_id
    else:
        payload["history"] = [{"item_id": "seed_item_a", "listening_count": 1}]
    response = requests.post(f"{API_URL}/recommend", json=payload, timeout=10)
    response.raise_for_status()
    st.json(response.json())
