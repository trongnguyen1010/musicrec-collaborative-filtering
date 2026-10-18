"""Streamlit prototype consuming the verified release through the REST API."""

import json
import os

import requests
import streamlit as st

API_URL = os.getenv("MUSICREC_API_URL", "http://127.0.0.1:8000")
st.set_page_config(page_title="MusicRec", page_icon="🎵")
st.title("Khám phá nghệ sĩ cùng MusicRec")
user_id = st.text_input("Mã người dùng đã có (không bắt buộc)")
raw_history = st.text_area(
    "Nghệ sĩ đã nghe và số lượt nghe, mỗi dòng một cặp mã,lượt nghe", placeholder="102,5\n204,2"
)
k = st.slider("Số nghệ sĩ gợi ý", min_value=1, max_value=20, value=10)
st.caption("Để trống hồ sơ để xem nghệ sĩ phổ biến.")
if st.button("Tạo gợi ý"):
    try:
        payload: dict[str, object] = {"k": k}
        if user_id.strip():
            payload["user_id"] = user_id.strip()
        if raw_history.strip():
            entries = []
            for line in raw_history.splitlines():
                if not line.strip():
                    continue
                item, count = line.rsplit(",", 1)
                entries.append({"item_id": item.strip(), "listening_count": float(count)})
            payload["history"] = entries
        with st.spinner("Đang tìm nghệ sĩ phù hợp…"):
            response = requests.post(
                f"{API_URL}/recommend",
                data=json.dumps(payload),
                headers={"Content-Type": "application/json"},
                timeout=30,
            )
            response.raise_for_status()
        result = response.json()
        if result["fallback_used"]:
            st.info(
                "Gợi ý đang dùng hồ sơ đầu vào hoặc phương án dự phòng. "
                "Với hồ sơ trống, danh sách là các nghệ sĩ phổ biến."
            )
        rows = [
            {
                "Vị trí": rank,
                "Nghệ sĩ": row.get("name") or row["item_id"],
                "Mã nghệ sĩ": row["item_id"],
                "Vì sao": (
                    "Được nhiều người nghe trong dữ liệu"
                    if "popularity" in row["reason"]
                    else "Gợi ý từ lịch sử nghe và tiêu chí khám phá"
                ),
            }
            for rank, row in enumerate(result["recommendations"], 1)
        ]
        if rows:
            st.dataframe(rows, hide_index=True, use_container_width=True)
        else:
            st.info("Không còn nghệ sĩ phù hợp trong danh mục để gợi ý.")
    except (ValueError, KeyError):
        st.error("Hãy nhập mỗi dòng theo dạng mã nghệ sĩ,số lượt nghe dương.")
    except requests.RequestException:
        st.error(
            "Chưa nhận được kết quả. Hãy kiểm tra kết nối hoặc trạng thái sẵn sàng của mô hình."
        )
