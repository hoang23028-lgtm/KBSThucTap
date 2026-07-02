# Cải Tiến Dự Án — Hệ Thống Gợi Ý Chuyên Ngành CNTT

Tổng hợp các thay đổi và hướng phát triển đã thực hiện cho dự án.

## Summary of Improvements

- Migrate từ TinyDB → SQLite cho rules/history (mạnh hơn về transaction).
- Thêm in-memory caching cho rules và prediction.
- Tối ưu index cho các bảng SQLite liên quan.
- Thêm hyperparameter tuning cho Random Forest (RandomizedSearchCV).

## Key Changes

- `src/database.py`: wrapper SQLite, schema, migration helper.
- `src/cache.py`: `PredictionCache`, `RulesCache`, `QueryCache`.
- `src/ml_model.py`: huấn luyện với tuning, lưu metrics và best_params.

## How to Verify

1. Migrate dữ liệu (nếu thích):

```bash
python scripts/migrate_to_sqlite.py
```

2. Huấn luyện và kiểm tra metrics:

```bash
python scripts/train.py
```

3. Kiểm tra rules count:

```bash
python -c "from src.expert_system import ExpertSystem; print(len(ExpertSystem().get_all_rules()))"
```

## Project file reference

```text
src/
├── cache.py
├── config.py
├── database.py
├── data_loader.py
├── expert_system.py
├── hybrid_engine.py
└── ml_model.py
```

## Next Steps

- Async inference engine
- Caching phân tán (Redis) cho scale
- Tự động retrain khi có dữ liệu mới
- Sử dụng Optuna cho tuning nâng cao
- Xây dựng API (FastAPI) cho production

---
Last updated: 2026-06-29
