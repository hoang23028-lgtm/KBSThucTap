"""Dashboard thống kê dữ liệu và đánh giá mô hình ML."""

import utils  # noqa: F401

import streamlit as st

from src.config import COURSE_LABELS_VI, MAJOR_LABELS_VI, MODELS_DIR
from src.data_loader import get_dataset_summary, load_raw_data
from src.ml_model import MajorClassifier
from utils.charts import (
    confusion_matrix_chart,
    feature_importance_chart,
    gpa_histogram,
    major_distribution_chart,
    score_heatmap,
)

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

st.title("📊 Dashboard Đánh giá")
st.caption("Thống kê bộ dữ liệu và hiệu suất mô hình Random Forest")


@st.cache_data
def load_data():
    return load_raw_data()


@st.cache_resource
def load_classifier(model_mtime):
    return MajorClassifier.load()


df = load_data()
model_path = MODELS_DIR / "random_forest.joblib"
model_mtime = model_path.stat().st_mtime if model_path.exists() else None
clf = load_classifier(model_mtime)
summary = get_dataset_summary(df)

st.subheader("Tổng quan dữ liệu")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Số sinh viên", summary["total_students"])
m2.metric("Bản ghi điểm", f"{summary['total_records']:,}")
m3.metric("GPA trung bình", summary["gpa_mean"])
m4.metric("Độ lệch GPA", summary["gpa_std"])

tab_data, tab_model = st.tabs(["📁 Phân tích dữ liệu", "🤖 Đánh giá mô hình"])

with tab_data:
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(major_distribution_chart(df), use_container_width=True)
    with c2:
        st.plotly_chart(gpa_histogram(df), use_container_width=True)

    st.plotly_chart(score_heatmap(df), use_container_width=True)

    st.subheader("Phân bố theo chuyên ngành")
    major_rows = [
        {"Chuyên ngành": MAJOR_LABELS_VI.get(k, k), "Số SV": v}
        for k, v in summary["majors"].items()
    ]
    st.dataframe(major_rows, use_container_width=True, hide_index=True)

    st.subheader("Điểm trung bình theo môn")
    score_rows = [
        {"Môn học": COURSE_LABELS_VI.get(k, k), "Điểm TB": v}
        for k, v in summary["score_mean_by_course"].items()
    ]
    st.dataframe(score_rows, use_container_width=True, hide_index=True)

with tab_model:
    metrics = clf.metrics
    if not metrics:
        st.warning("Mô hình chưa có metrics. Chạy: `python scripts/train.py`")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Accuracy", f"{metrics.get('accuracy', 0)*100:.1f}%")
        c2.metric("F1-macro", f"{metrics.get('f1_macro', 0)*100:.1f}%")
        c3.metric("CV Accuracy", f"{metrics.get('cv_mean', 0)*100:.1f}%")
        c4.metric("CV Std", f"±{metrics.get('cv_std', 0)*100:.2f}%")

        st.markdown(
            f"- Tập huấn luyện: **{metrics.get('train_size', '—')}** mẫu\n"
            f"- Tập kiểm tra: **{metrics.get('test_size', '—')}** mẫu\n"
            f"- Thuật toán: **Random Forest** ({clf.best_params.get('n_estimators', 200)} cây, max_depth={clf.best_params.get('max_depth', 'auto')}, max_features={clf.best_params.get('max_features', 'auto')}, class_weight={clf.best_params.get('class_weight', 'balanced')})"
        )

        st.subheader("Thông số mô hình tốt nhất")
        best_params_table = [
            {"Thuộc tính": k, "Giá trị": str(v)}
            for k, v in clf.best_params.items()
        ]
        st.dataframe(best_params_table, use_container_width=True, hide_index=True)

        col_a, col_b = st.columns(2)
        with col_a:
            if clf.feature_importance:
                st.plotly_chart(
                    feature_importance_chart(clf.feature_importance),
                    use_container_width=True,
                )
        with col_b:
            if clf.confusion is not None:
                st.plotly_chart(
                    confusion_matrix_chart(clf.confusion),
                    use_container_width=True,
                )

        if clf.classification_report_str:
            st.subheader("Báo cáo phân loại (Classification Report)")
            st.code(clf.classification_report_str, language="text")

        st.subheader("Tổng quan đánh giá mô hình")
        st.markdown(
            f"- CV Accuracy trung bình: **{metrics.get('cv_mean', 0)*100:.1f}%**\n"
            f"- Độ lệch CV: **±{metrics.get('cv_std', 0)*100:.2f}%**\n"
            f"- Accuracy trên test set: **{metrics.get('accuracy', 0)*100:.1f}%**\n"
            f"- F1-macro trên test set: **{metrics.get('f1_macro', 0)*100:.1f}%**"
        )

    st.divider()
    if st.button("🔄 Huấn luyện lại mô hình", type="secondary"):
        with st.spinner("Đang huấn luyện Random Forest..."):
            new_clf = MajorClassifier()
            new_metrics = new_clf.train()
            new_clf.save()
            st.cache_resource.clear()
            st.success(
                f"Huấn luyện xong! Accuracy: {new_metrics['accuracy']*100:.1f}% | "
                f"F1: {new_metrics['f1_macro']*100:.1f}%"
            )
            st.rerun()
