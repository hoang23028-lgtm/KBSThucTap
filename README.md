# Hệ thống Gợi ý Chuyên ngành CNTT (Hybrid Knowledge System)

Đồ án tốt nghiệp — Hệ thống lai **Expert System + Random Forest** gợi ý chuyên ngành dựa trên điểm số môn học.

## Kiến trúc

| Thành phần | Công nghệ | Vai trò |
|---|---|---|
| AI Layer | Random Forest (scikit-learn) | Phân tích pattern điểm số, dự đoán xác suất |
| Expert Layer | TinyDB + Rule Engine | Lưu trữ & suy diễn tập luật tri thức miền |
| Hybrid Engine | Trọng số 60% AI + 40% Chuyên gia | Kết hợp & giải thích (XAI) |
| Giao diện | Streamlit | Form nhập điểm, dashboard, quản trị luật |

## Cài đặt & chạy

```bash
pip install -r requirements.txt
python scripts/train.py
streamlit run app/main.py
```

## Cấu trúc thư mục

```
ThucTapTotNghiep/
├── app/                        # Giao diện Streamlit
│   ├── main.py                 # Trang chủ
│   ├── pages/                  # Các trang chức năng
│   └── utils/
│       └── charts.py           # Biểu đồ Plotly
├── src/                        # Logic nghiệp vụ
│   ├── config.py               # Cấu hình, hằng số
│   ├── data_loader.py          # Tiền xử lý CSV
│   ├── db.py                   # TinyDB (UTF-8)
│   ├── expert_system.py        # Hệ chuyên gia + luật
│   ├── ml_model.py             # Random Forest
│   └── hybrid_engine.py        # Bộ suy diễn lai
├── data/
│   ├── raw/data.csv            # Dữ liệu gốc (895 SV)
│   ├── rules/rules.json        # Tập luật TinyDB
│   └── history/                # Lịch sử gợi ý
├── models/
│   └── random_forest.joblib    # Mô hình đã huấn luyện
├── scripts/
│   └── train.py                # Huấn luyện mô hình
├── requirements.txt
└── README.md
```

## Chức năng

| Trang | Mô tả |
|---|---|
| Gợi ý chuyên ngành | Nhập điểm, XAI, so sánh AI / chuyên gia / lai |
| Dashboard | Thống kê dữ liệu, confusion matrix, feature importance |
| Quản trị luật | CRUD tập luật TinyDB (mật khẩu: `admin123`) |

## 7 chuyên ngành

Khoa học Dữ liệu · IoT · Công nghệ CSDL · Hệ thống Thông minh · Công nghệ Game · Công nghệ Mạng · Kỹ thuật Phần mềm
