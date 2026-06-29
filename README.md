# Hệ thống Gợi ý Chuyên ngành CNTT

Dự án tốt nghiệp: hệ thống gợi ý chuyên ngành kết hợp **Expert System** và **Random Forest** để đề xuất chuyên ngành dựa trên điểm thi và luật chuyên gia.

## Kiến trúc hiện tại

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| AI Layer | Random Forest (scikit-learn) | Dự đoán chuyên ngành từ dữ liệu điểm số |
| Expert Layer | SQLite + Rule Engine | Quản lý luật, suy diễn và giải thích gợi ý |
| Hybrid Engine | Kết hợp Expert + ML | So sánh và trộn kết quả đề xuất |
| Giao diện | Streamlit | Nhập điểm, dashboard, quản trị luật |

## Cài đặt và chạy

```bash
pip install -r requirements.txt
python scripts/train_v2.py
streamlit run app/main.py
```

> Chạy lệnh từ thư mục gốc của dự án để `Streamlit` và `src` được nhận đúng đường dẫn.

## Cấu trúc thư mục

```text
ThucTapTotNghiep/
├── app/
│   ├── main.py
│   ├── pages/
│   │   ├── 1_Goi_y_chuyen_nganh.py
│   │   ├── 2_Dashboard.py
│   │   └── 3_Quan_tri_luat.py
│   └── utils/
│       └── charts.py
├── src/
│   ├── cache.py
│   ├── config.py
│   ├── database.py
│   ├── data_loader.py
│   ├── expert_system_v2.py
│   ├── hybrid_engine_v2.py
│   └── ml_model_v2.py
├── data/
│   ├── history/
│   │   └── recommendations.db
│   ├── processed/
│   ├── raw/
│   │   └── data.csv
│   └── rules/
│       └── rules.db
├── models/
│   └── random_forest.joblib
├── scripts/
│   ├── migrate_to_sqlite.py
│   ├── train_v2.py
│   └── train.py
├── requirements.txt
├── README.md
├── QUICKSTART.md
└── IMPROVEMENTS.md
```

## Chức năng chính

- Gợi ý chuyên ngành dựa trên điểm môn học
- So sánh kết quả AI / chuyên gia / hybrid
- Quản trị luật theo SQLite
- Dashboard đánh giá mô hình và thống kê dữ liệu

## Các chuyên ngành hỗ trợ

Khoa học Dữ liệu · IoT · Công nghệ CSDL · Hệ thống Thông minh · Công nghệ Game · Công nghệ Mạng · Kỹ thuật Phần mềm

