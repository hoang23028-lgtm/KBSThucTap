"""Trang gợi ý chuyên ngành cho sinh viên."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import utils  # noqa: F401

import pandas as pd
import streamlit as st

from src.config import COURSE_LABELS_VI, COURSES, MAJOR_LABELS_VI
from src.data_loader import load_raw_data
from src.hybrid_engine_v2 import HybridRecommendationEngine
from utils.charts import method_comparison_chart, recommendation_bar_chart

st.set_page_config(page_title="Gợi ý chuyên ngành", page_icon="🎯", layout="wide")

st.title("🎯 Gợi ý Chuyên ngành")
st.caption("Nhập điểm các môn học cốt lõi để nhận gợi ý từ hệ thống lai AI + Chuyên gia")


@st.cache_resource
def get_engine():
    return HybridRecommendationEngine()


engine = get_engine()


def render_score_inputs(default_scores: dict | None = None) -> dict:
    default_scores = default_scores or {c: 75.0 for c in COURSES}
    scores = {}
    cols = st.columns(2)
    for i, course in enumerate(COURSES):
        label = COURSE_LABELS_VI.get(course, course)
        with cols[i % 2]:
            scores[course] = st.slider(
                label,
                min_value=0.0,
                max_value=100.0,
                value=float(default_scores.get(course, 75.0)),
                step=0.5,
                key=f"score_{course}",
            )
    return scores


with st.sidebar:
    st.header("⚡ Tùy chọn nhanh")
    st.markdown("**Tải mẫu từ dữ liệu**")
    sample_id = st.text_input("Mã sinh viên mẫu", value="ST161400", help="VD: ST161400")
    if st.button("Nạp điểm mẫu", use_container_width=True):
        raw = load_raw_data()
        sample = raw[raw["student_id"] == sample_id]
        if sample.empty:
            st.error(f"Không tìm thấy sinh viên {sample_id}")
        else:
            st.session_state["sample_scores"] = dict(zip(sample["course_name"], sample["score"]))
            st.session_state["sample_gpa"] = sample["gpa"].iloc[0]
            st.session_state["sample_major"] = sample["major"].iloc[0]
            st.success(f"Đã nạp điểm của {sample_id}")

    st.divider()
    student_id = st.text_input("Mã sinh viên (tùy chọn)", value="", placeholder="VD: SV2024001")
    save_history = st.checkbox("Lưu lịch sử gợi ý", value=True)

default = st.session_state.get("sample_scores")
scores = render_score_inputs(default)

if "sample_major" in st.session_state:
    actual = st.session_state["sample_major"]
    gpa = st.session_state.get("sample_gpa", "—")
    st.info(
        f"📌 Mẫu thực tế: **{MAJOR_LABELS_VI.get(actual, actual)}** | GPA: **{gpa}** "
        f"(dùng để so sánh, không ảnh hưởng gợi ý)"
    )

if st.button("🔍 Phân tích & Gợi ý chuyên ngành", type="primary", use_container_width=True):
    with st.spinner("Đang suy diễn (AI + Hệ chuyên gia)..."):
        result = engine.recommend(
            scores,
            student_id=student_id,
            save_history=save_history,
        )
        comparison = engine.compare_methods(scores)

    st.session_state["last_result"] = result
    st.session_state["last_comparison"] = comparison

if "last_result" in st.session_state:
    result = st.session_state["last_result"]
    comparison = st.session_state.get("last_comparison", {})

    st.divider()
    top = result["recommended_major"]
    conf = result["confidence"] * 100

    c1, c2, c3 = st.columns([2, 1, 1])
    with c1:
        st.success(
            f"### ✅ Gợi ý: {result['recommended_major_vi']}\n"
            f"**Độ tin cậy:** {conf:.1f}%"
        )
    with c2:
        ai_top = MAJOR_LABELS_VI.get(result["ai_prediction"], result["ai_prediction"])
        st.metric("Chỉ AI", ai_top)
    with c3:
        st.metric(
            "Chỉ chuyên gia",
            MAJOR_LABELS_VI.get(comparison.get("expert_only", "—"), comparison.get("expert_only", "—")),
        )

    tab1, tab2, tab3, tab4 = st.tabs(["📊 Biểu đồ", "💬 Giải thích XAI", "📋 Luật kích hoạt", "⚖️ So sánh phương pháp"])

    with tab1:
        st.plotly_chart(recommendation_bar_chart(result["ranking"]), use_container_width=True)

        rank_df = pd.DataFrame(result["ranking"])
        rank_df = rank_df[["major_vi", "final_score", "ai_score", "expert_score"]]
        rank_df.columns = ["Chuyên ngành", "Lai", "AI", "Chuyên gia"]
        rank_df["Lai"] = (rank_df["Lai"] * 100).round(1).astype(str) + "%"
        rank_df["AI"] = (rank_df["AI"] * 100).round(1).astype(str) + "%"
        rank_df["Chuyên gia"] = (rank_df["Chuyên gia"] * 100).round(1).astype(str) + "%"
        st.dataframe(rank_df, use_container_width=True, hide_index=True)

    with tab2:
        st.subheader("Giải thích kết quả (Explainable AI)")
        for line in result["explanations"]:
            st.markdown(line)

        st.subheader("Môn học ảnh hưởng mạnh nhất (Feature Importance)")
        for feat in result["top_features"]:
            st.progress(
                min(feat["importance"], 1.0),
                text=f"{feat['course_vi']}: {feat['score']:.0f}đ (importance: {feat['importance']:.3f})",
            )

    with tab3:
        fired = result["fired_rules"]
        if not fired:
            st.warning("Không có luật chuyên gia nào được kích hoạt với bộ điểm này.")
        else:
            for rule in fired:
                icon = "🚫" if rule["action_type"] == "exclude" else "✅"
                action = "Loại trừ" if rule["action_type"] == "exclude" else f"Cộng +{rule['weight']*100:.0f}%"
                st.markdown(
                    f"{icon} **Luật #{rule['rule_id']} — {rule['name']}**\n\n"
                    f"{rule['description']}\n\n"
                    f"→ {action} **{MAJOR_LABELS_VI.get(rule['target_major'], rule['target_major'])}**"
                )
                st.divider()

    with tab4:
        if comparison:
            st.plotly_chart(
                method_comparison_chart(
                    comparison["ai_proba"],
                    comparison["expert_proba"],
                    comparison["hybrid_proba"],
                ),
                use_container_width=True,
            )
            comp_data = {
                "Phương pháp": ["Chỉ AI", "Chỉ chuyên gia", "Lai (Hybrid)"],
                "Chuyên ngành": [
                    MAJOR_LABELS_VI.get(comparison["ai_only"], comparison["ai_only"]),
                    MAJOR_LABELS_VI.get(comparison["expert_only"], comparison["expert_only"]),
                    MAJOR_LABELS_VI.get(comparison["hybrid"], comparison["hybrid"]),
                ],
            }
            st.table(pd.DataFrame(comp_data))

st.divider()
with st.expander("📜 Lịch sử gợi ý gần đây"):
    history = engine.get_history(limit=10)
    if history:
        hist_df = pd.DataFrame(history)[
            ["timestamp", "student_id", "recommended_major", "confidence"]
        ]
        hist_df["recommended_major"] = hist_df["recommended_major"].map(
            lambda m: MAJOR_LABELS_VI.get(m, m)
        )
        hist_df["confidence"] = (hist_df["confidence"] * 100).round(1).astype(str) + "%"
        hist_df.columns = ["Thời gian", "Mã SV", "Gợi ý", "Tin cậy"]
        st.dataframe(hist_df, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có lịch sử gợi ý.")
