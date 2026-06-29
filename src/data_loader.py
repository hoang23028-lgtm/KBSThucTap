"""Tiền xử lý và tải dữ liệu sinh viên từ CSV."""

import pandas as pd

from src.config import COURSES, DATA_RAW


def load_raw_data(path=None) -> pd.DataFrame:
    path = path or DATA_RAW
    return pd.read_csv(path)


def pivot_student_scores(df: pd.DataFrame) -> pd.DataFrame:
    """Chuyển dữ liệu dạng dài sang ma trận điểm theo sinh viên."""
    pivot = df.pivot_table(
        index=["student_id", "major", "gpa"],
        columns="course_name",
        values="score",
        aggfunc="first",
    ).reset_index()

    for course in COURSES:
        if course not in pivot.columns:
            pivot[course] = 0.0

    return pivot


def build_training_dataset(path=None) -> tuple[pd.DataFrame, pd.Series, pd.DataFrame]:
    """Trả về X (điểm), y (chuyên ngành), và bảng đầy đủ."""
    raw = load_raw_data(path)
    wide = pivot_student_scores(raw)
    X = wide[COURSES].copy()
    y = wide["major"].copy()
    return X, y, wide


def get_dataset_summary(df: pd.DataFrame) -> dict:
    """Thống kê tổng quan phục vụ dashboard."""
    wide = pivot_student_scores(df)
    return {
        "total_students": wide["student_id"].nunique(),
        "total_records": len(df),
        "majors": wide["major"].value_counts().to_dict(),
        "gpa_mean": round(wide["gpa"].mean(), 2),
        "gpa_std": round(wide["gpa"].std(), 2),
        "score_mean_by_course": wide[COURSES].mean().round(2).to_dict(),
    }
