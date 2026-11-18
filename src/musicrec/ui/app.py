"""Fallback Streamlit demo; it only calls the REST API, never model code.

streamlit run src/musicrec/ui/app.py   (API at MUSICREC_API_URL, default 127.0.0.1:8000)
"""

import os
from typing import Any

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("MUSICREC_API_URL", "http://127.0.0.1:8000")
MODEL_LABELS = {
    "pure_svd": "PureSVD k=16",
    "m1": "M1 (tái xếp hạng trên PureSVD)",
    "implicit_als": "Implicit ALS (mở rộng)",
}


def get(path: str, **params: Any) -> Any:
    response = requests.get(f"{API_URL}{path}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def recommend(payload: dict[str, Any]) -> dict[str, Any]:
    response = requests.post(f"{API_URL}/recommend", json=payload, timeout=30)
    response.raise_for_status()
    result: dict[str, Any] = response.json()
    return result


def show(result: dict[str, Any]) -> None:
    if result["fallback_used"]:
        st.warning(f"Dùng phương án dự phòng: {result['fallback_reason']}")
    if result["ignored_item_ids"]:
        st.info(f"Nghệ sĩ ngoài danh mục M2: {', '.join(result['ignored_item_ids'])}")
    st.caption(
        f"Nhánh {result['branch']}, mô hình {result['model']}, "
        f"số người nghe trung bình {result['mean_listeners'] or 0:.1f}"
    )
    st.dataframe(
        pd.DataFrame(result["recommendations"])[["rank", "name", "listeners", "score", "reason"]],
        hide_index=True,
    )


st.set_page_config(page_title="MusicRec", page_icon="🎵", layout="wide")
st.title("MusicRec demo")
health = get("/health")
st.caption(f"Bản phát hành {health['model_version']}")
k = st.sidebar.slider("Số gợi ý K", min_value=5, max_value=20, value=10)
existing, new = st.tabs(["Người dùng có sẵn", "Người dùng mới"])

with existing:
    users = [u["user_id"] for u in get("/users", limit=2000)]
    user_id = st.selectbox("User ID", users)
    model = st.radio(
        "Mô hình", list(MODEL_LABELS), format_func=MODEL_LABELS.__getitem__, horizontal=True
    )
    compare = st.checkbox("So sánh PureSVD và M1 cạnh nhau", value=True)
    history = get(f"/users/{user_id}/history", limit=10)
    with st.expander(f"Lịch sử nghe ({history['total']} nghệ sĩ, 10 nghe nhiều nhất)"):
        st.dataframe(
            pd.DataFrame(history["items"])[["name", "listening_count", "split", "listeners"]],
            hide_index=True,
        )
    if compare:
        left, right = st.columns(2)
        for column, name in [(left, "pure_svd"), (right, "m1")]:
            with column:
                st.subheader(MODEL_LABELS[name])
                show(recommend({"user_id": user_id, "k": k, "model": name}))
    else:
        show(recommend({"user_id": user_id, "k": k, "model": model}))

with new:
    query = st.text_input("Tìm nghệ sĩ")
    options = {a["item_id"]: a["name"] for a in get("/artists", q=query, limit=50)}
    chosen = st.multiselect(
        "Chọn 1–5 nghệ sĩ bạn thích",
        list(options),
        format_func=options.__getitem__,
        max_selections=5,
    )
    show(recommend({"history": [{"item_id": i} for i in chosen], "k": k}))
