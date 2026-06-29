# Cải Tiến Dự Án — Hệ Thống Gợi Ý Chuyên Ngành CNTT

## 📊 Tổng quan cải tiến

Dự án đã được nâng cấp để sử dụng SQLite thay cho TinyDB, bổ sung caching, tối ưu truy vấn và thêm hyperparameter tuning cho mô hình ML.

## 1. SQLite thay TinyDB

- File mới: `src/database.py`
- Dữ liệu rules và history được lưu trong SQLite:
  - `data/rules/rules.db`
  - `data/history/recommendations.db`
- Schema tự động khởi tạo và tạo index.

### Lợi ích

- Tốc độ truy vấn nhanh hơn
- Hỗ trợ transaction và concurrency
- Dữ liệu nhất quán hơn
- Tăng khả năng mở rộng

## 2. Caching layer

- File: `src/cache.py`
- Thành phần chính:
  - `PredictionCache` — cache kết quả dự đoán
  - `RulesCache` — cache rules in-memory
  - `QueryCache` — cache truy vấn DB theo TTL

### Lợi ích

- Giảm thời gian trả lời cho truy vấn lặp lại
- Giảm tải database
- Tăng tốc inference của hệ chuyên gia

## 3. Tối ưu truy vấn database

- Thêm index cho bảng `rules` và `recommendations`
- Kết hợp cache và truy vấn index

### Lợi ích

- Truy vấn rules nhanh hơn
- Giảm I/O đĩa
- Cải thiện độ phản hồi của ứng dụng

## 4. Hyperparameter tuning cho mô hình ML

- File: `src/ml_model_v2.py`
- Sử dụng `RandomizedSearchCV` với 5-fold cross-validation
- Lưu `best_params`, `metrics`, và `classification_report`

### Lợi ích

- Tăng độ chính xác
- Cải thiện khả năng tổng quát hóa
- Ghi nhận kết quả training rõ ràng

## Cấu trúc file hiện tại

```text
src/
├── cache.py
├── config.py
├── database.py
├── data_loader.py
├── expert_system_v2.py
├── hybrid_engine_v2.py
└── ml_model_v2.py
```

## Hướng dẫn sử dụng

1. Migrate từ TinyDB sang SQLite:

```bash
python scripts/migrate_to_sqlite.py
```

2. Huấn luyện mô hình:

```bash
python scripts/train_v2.py
```

3. Chạy ứng dụng:

```bash
streamlit run app/main.py
```

## Ghi chú

- Chạy các lệnh từ thư mục gốc của dự án.
- Nếu còn dùng các file cũ, hãy migrate và kiểm tra lại nguồn dữ liệu.

## Hướng phát triển tiếp theo

- Async inference
- Caching phân tán (Redis)
- Tự động retrain với dữ liệu mới
- Bayesian tuning (Optuna)
- API bằng FastAPI
