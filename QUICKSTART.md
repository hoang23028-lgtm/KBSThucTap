# Quickstart

Hướng dẫn nhanh để chạy ứng dụng với SQLite và mô hình đã tune.

## 1. Migrate dữ liệu từ TinyDB sang SQLite

```bash
python scripts/migrate_to_sqlite.py
```

Kết quả:

- `data/rules/rules.db`
- `data/history/recommendations.db`

## 2. Huấn luyện mô hình với hyperparameter tuning

```bash
python scripts/train_v2.py
```

Kết quả:

- `models/random_forest.joblib` được cập nhật
- Best hyperparameters được lưu
- Metrics và classification report được ghi lại

## 3. Chạy ứng dụng Streamlit

```bash
streamlit run app/main.py
```

> Chạy lệnh từ thư mục gốc của dự án để `src` được import đúng.

## 4. Kiểm tra migration

```bash
python -c "import sqlite3; conn = sqlite3.connect('data/rules/rules.db'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM rules'); print('rules', cur.fetchone()[0]); conn.close();"
```

```bash
python -c "import sqlite3; conn = sqlite3.connect('data/history/recommendations.db'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM recommendations'); print('recommendations', cur.fetchone()[0]); conn.close();"
```

## 5. Cấu hình nhanh

- Thay đổi `max_size` trong `src/cache.py` nếu cần tối ưu bộ nhớ.
- Tăng `n_iter` trong `scripts/train_v2.py` để kiểm tra thêm nhiều tham số.

## 6. Troubleshooting

- `Database is locked`: đóng các kết nối SQLite trước khi migrate.
- `Module not found`: chạy từ root dự án hoặc xác nhận `PYTHONPATH`.
- `Cache hit rate is low`: tăng `PredictionCache.max_size` hoặc xóa cache.

## 7. Lệnh tóm tắt

```bash
python scripts/migrate_to_sqlite.py
python scripts/train_v2.py
streamlit run app/main.py
```
