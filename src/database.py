"""SQLite database layer cho rules và history."""

import json
import sqlite3
from pathlib import Path

from src.config import HISTORY_DB, RULES_DB


class SQLiteDB:
    """SQLite wrapper cho rules và recommendations history."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @property
    def _is_rules_db(self) -> bool:
        return self.db_path.name == "rules.db"

    def _init_schema(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("PRAGMA encoding = 'UTF-8'")

            if self._is_rules_db:
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
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_rules_target_major ON rules(target_major)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_rules_active ON rules(active)"
                )
            else:
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
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_recommendations_student ON recommendations(student_id)"
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_recommendations_major ON recommendations(recommended_major)"
                )

            conn.commit()

    def insert(self, doc: dict) -> int:
        with sqlite3.connect(self.db_path) as conn:
            if self._is_rules_db:
                cursor = conn.execute(
                    """
                    INSERT INTO rules
                    (name, description, conditions, logic, action_type, target_major, weight, active)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        doc.get("name"),
                        doc.get("description"),
                        json.dumps(doc.get("conditions")),
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

    def all(self, limit: int | None = None) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if self._is_rules_db:
                query = "SELECT * FROM rules ORDER BY id"
            else:
                query = "SELECT * FROM recommendations ORDER BY timestamp DESC"
                if limit is not None:
                    query += f" LIMIT {int(limit)}"

            cursor = conn.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_by_id(self, doc_id: int) -> dict | None:
        table = self._table_name()
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(f"SELECT * FROM {table} WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update(self, doc_id: int, updates: dict) -> None:
        with sqlite3.connect(self.db_path) as conn:
            if self._is_rules_db:
                if "conditions" in updates and isinstance(updates["conditions"], (list, dict)):
                    updates["conditions"] = json.dumps(updates["conditions"])
                if "active" in updates and isinstance(updates["active"], bool):
                    updates["active"] = 1 if updates["active"] else 0
                set_clause = ", ".join(f"{k} = ?" for k in updates)
                values = list(updates.values()) + [doc_id]
                conn.execute(
                    f"UPDATE rules SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    values,
                )
            conn.commit()

    def remove(self, doc_id: int) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"DELETE FROM {self._table_name()} WHERE id = ?", (doc_id,))
            conn.commit()

    def truncate(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(f"DELETE FROM {self._table_name()}")
            conn.commit()

    def search(self, **kwargs) -> list[dict]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            if self._is_rules_db and "target_major" in kwargs:
                cursor = conn.execute(
                    "SELECT * FROM rules WHERE target_major = ? AND active = 1",
                    (kwargs["target_major"],),
                )
            else:
                cursor = conn.execute(f"SELECT * FROM {self._table_name()}")

            return [dict(row) for row in cursor.fetchall()]

    def count(self) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(f"SELECT COUNT(*) FROM {self._table_name()}")
            return cursor.fetchone()[0]

    def _table_name(self) -> str:
        return "rules" if self._is_rules_db else "recommendations"


def open_db(path: Path | None = None, *, rules: bool = True) -> SQLiteDB:
    """Mở database rules hoặc history."""
    if path is None:
        path = RULES_DB if rules else HISTORY_DB
    return SQLiteDB(path)
