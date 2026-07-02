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
python scripts/train.py               # huấn luyện và lưu model (nếu chưa có)
$env:ADMIN_PASSWORD = "your-password" # Windows — bắt buộc cho trang Quản trị
streamlit run app/main.py             # khởi động web UI
```

> Database SQLite (`data/rules/rules.db`, `data/history/recommendations.db`) được tạo tự động khi chạy lần đầu. Nếu `rules.db` trống, hệ thống sẽ seed luật mặc định.

### Mật khẩu quản trị

Trang **Quản trị luật** yêu cầu `ADMIN_PASSWORD` qua biến môi trường (xem `.env.example`) hoặc `.streamlit/secrets.toml`:

```toml
ADMIN_PASSWORD = "your-password"
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
├── app/                    # Streamlit app + pages + utils/charts
├── src/                    # Core: config, database, expert, hybrid, ml, cache
│   ├── default_rules.py    # Luật mặc định (tách riêng)
│   └── rule_utils.py       # Parse/chuẩn hóa luật
├── data/
│   ├── raw/data.csv
│   ├── rules/rules.db
│   └── history/recommendations.db
├── models/random_forest.joblib
├── scripts/                # train, analyze_rules_quality, ...
├── requirements.txt
└── README.md
```

## Usage

- Huấn luyện: `python scripts/train.py`
- Chạy app: `streamlit run app/main.py`
- Phân tích luật: `python scripts/analyze_rules_quality.py`

## Development

- Thực hiện thay đổi trong `src/`, chạy test nhỏ bằng script trong `scripts/`.
- Chức năng tự động "khôi phục luật mặc định" đã bị vô hiệu hóa trong giao diện quản trị. Nếu cần ghi đè, gọi `ExpertSystem().seed_default_rules()` thủ công (sao lưu `data/rules/rules.db` trước).

## Verification

```bash
python -c "from src.expert_system import ExpertSystem; print(len(ExpertSystem().get_all_rules()), 'rules')"
python -c "from src.ml_model import MajorClassifier; print(MajorClassifier.load().metrics)"
```

## Contributing

- Vui lòng mở pull request cho các thay đổi chức năng.
- Giữ style code nhất quán và cập nhật `README` nếu thay đổi cấu trúc.

## License & Contact

- License: (nếu cần) thêm file `LICENSE` ở root.
- Liên hệ: chủ dự án trên GitHub: `https://github.com/hoang23028-lgtm/KBSThucTap`

---
Last updated: 2026-07-02
