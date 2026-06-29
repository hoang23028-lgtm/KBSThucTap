"""Hệ thống gợi ý chuyên ngành lai: Expert System + Random Forest."""

import utils  # noqa: F401

import streamlit as st

st.set_page_config(
    page_title="Gợi ý Chuyên ngành CNTT",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🎓 Hệ thống Gợi ý Chuyên ngành CNTT")
st.markdown(
    """
    **Hệ thống tri thức lai (Hybrid Knowledge System)** kết hợp:
    - 🤖 **Trí tuệ nhân tạo** — Random Forest phân tích pattern điểm số
    - 📋 **Hệ chuyên gia** — Tập luật tri thức miền (TinyDB)
    - ⚖️ **Bộ suy diễn lai** — Kết hợp có trọng số, giải thích minh bạch (XAI)
    """
)

col1, col2, col3 = st.columns(3)
with col1:
    st.info("**Sinh viên** → Nhập điểm và nhận gợi ý chuyên ngành kèm lời giải thích.")
with col2:
    st.success("**Dashboard** → Thống kê dữ liệu, đánh giá mô hình ML, ma trận lỗi.")
with col3:
    st.warning("**Quản trị** → CRUD tập luật chuyên gia trực tiếp trên giao diện.")

st.divider()

st.subheader("Kiến trúc hệ thống")

st.markdown(
    """
```mermaid
flowchart LR
    A[Nhập điểm môn học] --> B[Random Forest]
    A --> C[Hệ chuyên gia TinyDB]
    B --> D[Bộ suy diễn lai]
    C --> D
    D --> E[Gợi ý + Giải thích XAI]
```
"""
)

st.subheader("7 chuyên ngành được hỗ trợ")

from src.config import MAJOR_LABELS_VI

majors_text = " · ".join(f"**{v}**" for v in MAJOR_LABELS_VI.values())
st.markdown(majors_text)

st.divider()
st.caption("Đồ án tốt nghiệp — Hệ thống lai Expert System + Machine Learning | Chọn trang ở sidebar ←")
