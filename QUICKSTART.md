# Quickstart

Hướng dẫn nhanh để chạy ứng dụng (migrate → train → run).

## Prerequisites

- Python 3.9+
- Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

## 1. Migrate dữ liệu (nếu cần)

```bash
python scripts/migrate_to_sqlite.py
```

Kết quả: tạo `data/rules/rules.db` và `data/history/recommendations.db`.

## 2. Huấn luyện mô hình

```bash
python scripts/train_v2.py
```

Kết quả:

- Cập nhật `models/random_forest.joblib`
- In ra best hyperparameters và metrics

## 3. Chạy ứng dụng Streamlit

```bash
streamlit run app/main.py
```

> Luôn chạy từ thư mục gốc để `src` được import chính xác.

## 4. Kiểm tra database

```bash
python -c "import sqlite3; conn = sqlite3.connect('data/rules/rules.db'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM rules'); print('rules', cur.fetchone()[0]); conn.close();"

python -c "import sqlite3; conn = sqlite3.connect('data/history/recommendations.db'); cur = conn.cursor(); cur.execute('SELECT COUNT(*) FROM recommendations'); print('recommendations', cur.fetchone()[0]); conn.close();"
```

## 5. Quick config tweaks

- Thay `max_size` trong `src/cache.py` để điều chỉnh bộ nhớ cache.
- Tăng `n_iter` trong `scripts/train_v2.py` để thử thêm lựa chọn hyperparameters.

## 6. Troubleshooting

- `Database is locked`: đóng các kết nối SQLite trước khi migrate.
- `ModuleNotFoundError`: chạy lệnh từ thư mục gốc hoặc kiểm tra `PYTHONPATH`.

## 7. Commands summary

```bash
python scripts/migrate_to_sqlite.py
python scripts/train_v2.py
streamlit run app/main.py
```
