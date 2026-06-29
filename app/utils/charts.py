"""Biểu đồ Plotly phục vụ giao diện Streamlit."""

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.config import COURSE_LABELS_VI, COURSES, MAJOR_LABELS_VI, MAJORS
from src.data_loader import pivot_student_scores


def major_distribution_chart(df: pd.DataFrame) -> go.Figure:
    wide = pivot_student_scores(df)
    counts = wide["major"].value_counts().reset_index()
    counts.columns = ["major", "count"]
    counts["major_vi"] = counts["major"].map(lambda m: MAJOR_LABELS_VI.get(m, m))
    fig = px.pie(
        counts,
        names="major_vi",
        values="count",
        title="Phân bố sinh viên theo chuyên ngành",
        hole=0.35,
    )
    fig.update_layout(legend_title_text="Chuyên ngành")
    return fig


def gpa_histogram(df: pd.DataFrame) -> go.Figure:
    wide = pivot_student_scores(df)
    fig = px.histogram(
        wide,
        x="gpa",
        nbins=25,
        title="Phân bố GPA sinh viên",
        labels={"gpa": "GPA", "count": "Số lượng"},
        color_discrete_sequence=["#2563eb"],
    )
    return fig


def score_heatmap(df: pd.DataFrame) -> go.Figure:
    wide = pivot_student_scores(df)
    means = wide[COURSES].mean().sort_values(ascending=False)
    labels = [COURSE_LABELS_VI.get(c, c) for c in means.index]
    fig = go.Figure(
        data=go.Heatmap(
            z=[means.values],
            x=labels,
            y=["Điểm TB"],
            colorscale="Blues",
            text=[[f"{v:.1f}" for v in means.values]],
            texttemplate="%{text}",
            showscale=True,
        )
    )
    fig.update_layout(title="Điểm trung bình theo môn học", height=280)
    return fig


def feature_importance_chart(importance: dict) -> go.Figure:
    items = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    courses = [COURSE_LABELS_VI.get(c, c) for c, _ in items]
    values = [v for _, v in items]
    fig = px.bar(
        x=values,
        y=courses,
        orientation="h",
        title="Mức độ quan trọng đặc trưng (Random Forest)",
        labels={"x": "Importance", "y": "Môn học"},
        color=values,
        color_continuous_scale="Viridis",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"}, showlegend=False)
    return fig


def confusion_matrix_chart(confusion: np.ndarray) -> go.Figure:
    labels = [MAJOR_LABELS_VI.get(m, m) for m in MAJORS]
    fig = px.imshow(
        confusion,
        x=labels,
        y=labels,
        text_auto=True,
        color_continuous_scale="Blues",
        title="Ma trận nhầm lẫn (Confusion Matrix)",
        labels={"x": "Dự đoán", "y": "Thực tế"},
    )
    fig.update_layout(height=550)
    return fig


def recommendation_bar_chart(ranking: list[dict]) -> go.Figure:
    df = pd.DataFrame(ranking)
    df["label"] = df["major_vi"]
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            name="Kết quả lai",
            x=df["label"],
            y=df["final_score"],
            marker_color="#2563eb",
        )
    )
    fig.add_trace(
        go.Bar(
            name="AI",
            x=df["label"],
            y=df["ai_score"],
            marker_color="#16a34a",
            opacity=0.7,
        )
    )
    fig.add_trace(
        go.Bar(
            name="Chuyên gia",
            x=df["label"],
            y=df["expert_score"],
            marker_color="#ea580c",
            opacity=0.7,
        )
    )
    fig.update_layout(
        barmode="group",
        title="So sánh xác suất gợi ý theo phương pháp",
        yaxis_title="Xác suất",
        xaxis_tickangle=-35,
        height=420,
    )
    return fig


def method_comparison_chart(ai_proba: dict, expert_proba: dict, hybrid_proba: dict) -> go.Figure:
    labels = [MAJOR_LABELS_VI.get(m, m) for m in MAJORS]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=[ai_proba.get(m, 0) for m in MAJORS], theta=labels, fill="toself", name="Chỉ AI"))
    fig.add_trace(
        go.Scatterpolar(
            r=[expert_proba.get(m, 0) for m in MAJORS],
            theta=labels,
            fill="toself",
            name="Chỉ chuyên gia",
        )
    )
    fig.add_trace(
        go.Scatterpolar(
            r=[hybrid_proba.get(m, 0) for m in MAJORS],
            theta=labels,
            fill="toself",
            name="Lai (Hybrid)",
        )
    )
    fig.update_layout(
        polar={"radialaxis": {"visible": True, "range": [0, 1]}},
        title="Radar chart: So sánh 3 phương pháp suy diễn",
        height=480,
    )
    return fig
