"""SQLite database layer với support cho rules và history."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from src.config import RULES_DB, HISTORY_DB


class SQLiteDB:
    """SQLite wrapper cho rules và recommendations history."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _init_schema(self) -> None:
        """Khởi tạo schema database nếu chưa tồn tại."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA encoding = 'UTF-8'")
            
            if self.db_path.name == "rules.db":
                # Schema cho rules
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS rules (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        description TEXT,
                        conditions TEXT NOT NULL,
                        logic TEXT DEFAULT 'AND',
                        action_type TEXT NOT NULL,
                        target_major TEXT NOT NULL,
                        weight REAL NOT NULL,
                        active INTEGER DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                # Index cho tối ưu truy vấn
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_rules_target_major ON rules(target_major)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_rules_active ON rules(active)"
                )
            else:
                # Schema cho history recommendations
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS recommendations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        student_id TEXT,
                        scores TEXT NOT NULL,
                        recommended_major TEXT NOT NULL,
                        confidence REAL,
                        ranking TEXT,
                        fired_rules TEXT,
                        explanations TEXT
                    )
                    """
                )
                # Index để tìm kiếm nhanh theo student_id
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_recommendations_student ON recommendations(student_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_recommendations_major ON recommendations(recommended_major)"
                )
            
            conn.commit()

    def insert(self, doc: dict) -> int:
        """Thêm document vào database (simulate TinyDB insert)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if self.db_path.name == "rules.db":
                cursor = conn.execute(
                    """
                    INSERT INTO rules 
                    (name, description, conditions, logic, action_type, target_major, weight, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc.get("name"),
                        doc.get("description"),
                        str(doc.get("conditions")),
                        doc.get("logic", "AND"),
                        doc.get("action_type"),
                        doc.get("target_major"),
                        doc.get("weight"),
                        1 if doc.get("active", True) else 0,
                    ),
                )
            else:
                cursor = conn.execute(
                    """
                    INSERT INTO recommendations
                    (student_id, scores, recommended_major, confidence, ranking, fired_rules, explanations)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc.get("student_id"),
                        str(doc.get("scores")),
                        doc.get("recommended_major"),
                        doc.get("confidence"),
                        str(doc.get("ranking")),
                        str(doc.get("fired_rules")),
                        str(doc.get("explanations")),
                    ),
                )
            
            conn.commit()
            return cursor.lastrowid

    def all(self) -> list[dict]:
        """Lấy tất cả documents (simulate TinyDB all)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if self.db_path.name == "rules.db":
                cursor = conn.execute("SELECT * FROM rules WHERE active = 1")
            else:
                cursor = conn.execute("SELECT * FROM recommendations ORDER BY timestamp DESC")
            
            return [dict(row) for row in cursor.fetchall()]

    def update(self, doc_id: int, updates: dict) -> None:
        """Cập nhật document theo ID."""
        with sqlite3.connect(self.db_path) as conn:
            if self.db_path.name == "rules.db":
                set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
                values = list(updates.values()) + [doc_id]
                conn.execute(
                    f"UPDATE rules SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    values,
                )
            conn.commit()

    def remove(self, doc_id: int) -> None:
        """Xóa document theo ID."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"DELETE FROM {self._table_name()} WHERE id = ?", (doc_id,))
            conn.commit()

    def truncate(self) -> None:
        """Xóa tất cả dữ liệu."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"DELETE FROM {self._table_name()}")
            conn.commit()

    def search(self, **kwargs) -> list[dict]:
        """Tìm kiếm theo điều kiện (optimize queries)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if self.db_path.name == "rules.db" and "target_major" in kwargs:
                cursor = conn.execute(
                    "SELECT * FROM rules WHERE target_major = ? AND active = 1",
                    (kwargs["target_major"],),
                )
            else:
                cursor = conn.execute(f"SELECT * FROM {self._table_name()}")
            
            return [dict(row) for row in cursor.fetchall()]

    def count(self) -> int:
        """Đếm số records."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {self._table_name()}")
            return cursor.fetchone()[0]

    def _table_name(self) -> str:
        """Lấy tên bảng từ tên file."""
        return "rules" if self.db_path.name == "rules.db" else "recommendations"

    def close(self) -> None:
        """Đóng kết nối (nếu cần)."""
        pass


def open_db(path: Path, **kwargs) -> SQLiteDB:
    """Hàm wrapper tương tự TinyDB (compatibility)."""
    return SQLiteDB(path)
