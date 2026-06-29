# Hệ thống Gợi ý Chuyên ngành CNTT

Mô tả ngắn: dự án kết hợp một lớp Expert System (luật chuyên gia) và một mô hình Random Forest để gợi ý chuyên ngành cho sinh viên dựa trên điểm các môn học.

## Overview

Dự án cung cấp:
- Một engine chuyên gia lưu trữ luật trong SQLite và suy diễn (boost / exclude).
- Một mô hình máy học (Random Forest) được huấn luyện với hyperparameter tuning.
- Một hybrid engine kết hợp đầu ra của hai thành phần trên.
- Giao diện quản trị và dashboard bằng Streamlit.

## Prerequisites

- Python 3.9+ (khuyến nghị 3.10+)
- Các thư viện trong `requirements.txt` (scikit-learn, pandas, streamlit, joblib,...)

## Quick Setup

Chạy các lệnh sau từ thư mục gốc của dự án:

```bash
pip install -r requirements.txt
python scripts/migrate_to_sqlite.py   # (nếu cần migrate)
python scripts/train_v2.py            # huấn luyện và lưu model
streamlit run app/main.py             # khởi động web UI
```

## Architecture

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| AI Layer | Random Forest (scikit-learn) | Dự đoán chuyên ngành từ dữ liệu điểm số |
| Expert Layer | SQLite + Rule Engine | Quản lý luật, suy diễn và giải thích gợi ý |
| Hybrid Engine | Kết hợp Expert + ML | So sánh và trộn kết quả đề xuất |
| Giao diện | Streamlit | Nhập điểm, dashboard, quản trị luật |

## Project Structure

```text
ThucTapTotNghiep/
├── app/ (Streamlit app + pages)
├── src/ (core modules: cache, database, expert system, hybrid engine, ml)
├── data/ (raw, processed, rules, history)
├── models/ (trained model artifacts)
├── scripts/ (migration, training, analysis)
├── requirements.txt
├── README.md
├── QUICKSTART.md
└── IMPROVEMENTS.md
```

## Usage

- Migrate dữ liệu: `python scripts/migrate_to_sqlite.py`
- Huấn luyện: `python scripts/train_v2.py`
- Chạy app: `streamlit run app/main.py`

## Development

- Thực hiện thay đổi trong `src/`, chạy test nhỏ bằng script trong `scripts/`.
- Khi cập nhật luật, gọi `ExpertSystem().seed_default_rules()` để ghi vào `data/rules/rules.db`.

## Verification

- Kiểm tra model tồn tại: `ls models/random_forest.joblib`
- Kiểm tra rules: `python -c "from src.expert_system_v2 import ExpertSystem; print(len(ExpertSystem().get_all_rules()))"`

## Contributing

- Vui lòng mở pull request cho các thay đổi chức năng.
- Giữ style code nhất quán và cập nhật `README` nếu thay đổi cấu trúc.

## License & Contact

- License: (nếu cần) thêm file `LICENSE` ở root.
- Liên hệ: chủ dự án trên GitHub: `https://github.com/hoang23028-lgtm/KBSThucTap`

---
Last updated: 2026-06-29

