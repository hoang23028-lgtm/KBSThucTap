# Quickstart

Hướng dẫn nhanh để chạy ứng dụng (train → run).

## Prerequisites

- Python 3.9+
- Cài đặt dependencies:

```bash
pip install -r requirements.txt
```

## 1. Huấn luyện mô hình (nếu chưa có)

```bash
python scripts/train.py
```

Kết quả:

- Cập nhật `models/random_forest.joblib`
- In ra best hyperparameters và metrics
- Khởi tạo `data/rules/rules.db` nếu chưa tồn tại

## 2. Cấu hình mật khẩu quản trị

```powershell
# Windows PowerShell
$env:ADMIN_PASSWORD = "your-password"
```

Hoặc tạo `.streamlit/secrets.toml`:

```toml
ADMIN_PASSWORD = "your-password"
```

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
- Tăng `n_iter` trong `scripts/train.py` để thử thêm lựa chọn hyperparameters.

## 6. Troubleshooting

- `Database is locked`: đóng các kết nối SQLite trước khi chạy script khác.
- `ModuleNotFoundError`: chạy lệnh từ thư mục gốc hoặc kiểm tra `PYTHONPATH`.
- Trang Quản trị không đăng nhập được: kiểm tra `ADMIN_PASSWORD` đã được set.

## 7. Commands summary

```bash
python scripts/train.py
$env:ADMIN_PASSWORD = "your-password"
streamlit run app/main.py
```
