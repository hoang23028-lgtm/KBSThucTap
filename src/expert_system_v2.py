"""Hệ chuyên gia tối ưu với SQLite + caching."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from src.config import MAJORS, RULES_DB
from src.cache import rules_cache
from src.database import open_db


OPERATORS = {
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    "<": lambda a, b: a < b,
    "==": lambda a, b: a == b,
}


def _default_rules() -> list[dict]:
    """Luật chuyên gia khởi tạo theo tri thức miền CNTT."""
    return [
        {
            "name": "DS - Thống kê cao",
            "description": "Điểm Thống kê cơ bản >= 80 → tăng Khoa học Dữ liệu",
            "conditions": [{"course": "Basic Statistics", "operator": ">=", "value": 80}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "DATA SCIENCE",
            "weight": 0.15,
            "active": True,
        },
        {
            "name": "DS - Đại số tuyến tính cao",
            "description": "Điểm Đại số tuyến tính >= 82 → tăng Khoa học Dữ liệu",
            "conditions": [{"course": "Linear Algebra", "operator": ">=", "value": 82}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "DATA SCIENCE",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "DS - Loại trừ toán yếu",
            "description": "Điểm Giải tích < 60 → loại trừ Khoa học Dữ liệu",
            "conditions": [{"course": "Calculus", "operator": "<", "value": 60}],
            "logic": "AND",
            "action_type": "exclude",
            "target_major": "DATA SCIENCE",
            "weight": 0.0,
            "active": True,
        },
        {
            "name": "IS - AI cao",
            "description": "Điểm AI >= 80 → tăng Hệ thống Thông minh",
            "conditions": [{"course": "Artificial Intelligence", "operator": ">=", "value": 80}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "INTELLIGENT SYSTEM",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "IS - Thuật toán cao",
            "description": "AI >= 75 VÀ Thiết kế thuật toán >= 78 → tăng Hệ thống Thông minh",
            "conditions": [
                {"course": "Artificial Intelligence", "operator": ">=", "value": 75},
                {"course": "Algorithm Design and Analysis", "operator": ">=", "value": 78},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "INTELLIGENT SYSTEM",
            "weight": 0.15,
            "active": True,
        },
        {
            "name": "NET - Mạng cao",
            "description": "Điểm Mạng máy tính >= 82 → tăng Công nghệ Mạng",
            "conditions": [{"course": "Computer Networks", "operator": ">=", "value": 82}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "NETWORK TECHNOLOGY",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "NET - HĐH + Mạng",
            "description": "Hệ điều hành >= 78 VÀ Mạng >= 80 → tăng Công nghệ Mạng",
            "conditions": [
                {"course": "Operating System", "operator": ">=", "value": 78},
                {"course": "Computer Networks", "operator": ">=", "value": 80},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "NETWORK TECHNOLOGY",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "DB - CSDL cao",
            "description": "Điểm Công nghệ CSDL >= 82 → tăng Công nghệ CSDL",
            "conditions": [{"course": "Database Technology", "operator": ">=", "value": 82}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "DATABASE TECHNOLOGY",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "DB - CTDL cao",
            "description": "CSDL >= 78 VÀ Cấu trúc dữ liệu >= 78 → tăng Công nghệ CSDL",
            "conditions": [
                {"course": "Database Technology", "operator": ">=", "value": 78},
                {"course": "Data Structures", "operator": ">=", "value": 78},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "DATABASE TECHNOLOGY",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "IoT - Mạng + CSDL",
            "description": "Mạng >= 80 VÀ CSDL >= 80 → tăng IoT",
            "conditions": [
                {"course": "Computer Networks", "operator": ">=", "value": 80},
                {"course": "Database Technology", "operator": ">=", "value": 80},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "INTERNET OF THINGS",
            "weight": 0.15,
            "active": True,
        },
        {
            "name": "GAME - Web + OOP",
            "description": "Web >= 78 VÀ OOP >= 78 → tăng Công nghệ Game",
            "conditions": [
                {"course": "Web Development", "operator": ">=", "value": 78},
                {"course": "Object Oriented Programming", "operator": ">=", "value": 78},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "GAME TECHNOLOGY",
            "weight": 0.15,
            "active": True,
        },
        {
            "name": "SE - Thiết kế chương trình",
            "description": "Phương pháp thiết kế CT >= 78 → tăng Kỹ thuật Phần mềm",
            "conditions": [{"course": "Program Design Methods", "operator": ">=", "value": 78}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "SOFTWARE ENGINEERING",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "SE - OOP cao",
            "description": "OOP >= 80 → tăng Kỹ thuật Phần mềm",
            "conditions": [{"course": "Object Oriented Programming", "operator": ">=", "value": 80}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "SOFTWARE ENGINEERING",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "Loại trừ AI yếu cho IS",
            "description": "Điểm AI < 55 → loại trừ Hệ thống Thông minh",
            "conditions": [{"course": "Artificial Intelligence", "operator": "<", "value": 55}],
            "logic": "AND",
            "action_type": "exclude",
            "target_major": "INTELLIGENT SYSTEM",
            "weight": 0.0,
            "active": True,
        },
    ]


class ExpertSystem:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or RULES_DB
        self.db_path = self.db_path.with_suffix(".db")  # Convert to .db for SQLite
        self.db = open_db(self.db_path)
        
        # Khởi tạo rules nếu DB trống
        if self.db.count() == 0:
            self.seed_default_rules()
        
        # Load rules vào cache
        self._load_rules_to_cache()

    def _load_rules_to_cache(self) -> None:
        """Load tất cả rules vào in-memory cache (tối ưu truy vấn)."""
        import json
        all_rules = self.db.all()
        
        # Parse conditions từ string (nếu từ SQLite)
        for rule in all_rules:
            if isinstance(rule.get("conditions"), str):
                try:
                    rule["conditions"] = json.loads(rule["conditions"])
                except:
                    pass
        
        rules_cache.load(all_rules)

    def seed_default_rules(self) -> int:
        """Khởi tạo tập luật mặc định."""
        import json
        self.db.truncate()
        for rule in _default_rules():
            # Ensure conditions is JSON string for storage
            rule_copy = rule.copy()
            rule_copy["conditions"] = json.dumps(rule_copy["conditions"])
            self.db.insert(rule_copy)
        return self.db.count()

    def get_all_rules(self) -> list[dict]:
        """Lấy tất cả rules từ cache (tối ưu)."""
        import json
        rules = rules_cache.get_all()
        
        # Ensure conditions is dict (parse if string)
        result = []
        for rule in rules:
            rule_copy = dict(rule)
            if isinstance(rule_copy.get("conditions"), str):
                try:
                    rule_copy["conditions"] = json.loads(rule_copy["conditions"])
                except:
                    pass
            # Add doc_id for compatibility with admin UI (TinyDB-style)
            rule_copy["doc_id"] = rule_copy.get("id", rule_copy.get("doc_id"))
            result.append(rule_copy)
        
        return result

    def add_rule(self, rule: dict) -> int:
        """Thêm luật mới."""
        import json
        rule_copy = rule.copy()
        rule_copy["conditions"] = json.dumps(rule_copy["conditions"])
        rule_id = self.db.insert(rule_copy)
        rules_cache.invalidate()  # Invalidate cache sau khi thêm
        self._load_rules_to_cache()
        return rule_id

    def update_rule(self, rule_id: int, updates: dict) -> None:
        """Cập nhật luật."""
        self.db.update(rule_id, updates)
        rules_cache.invalidate()
        self._load_rules_to_cache()

    def delete_rule(self, rule_id: int) -> None:
        """Xóa luật."""
        self.db.remove(rule_id)
        rules_cache.invalidate()
        self._load_rules_to_cache()

    def get_rule(self, rule_id: int) -> Optional[dict]:
        """Lấy một luật theo ID."""
        for rule in self.get_all_rules():
            if rule.get("id") == rule_id or rule.get("doc_id") == rule_id:
                return rule
        return None

    def toggle_rule(self, rule_id: int, active: bool) -> None:
        """Kích hoạt/vô hiệu hóa luật."""
        self.db.update(rule_id, {"active": 1 if active else 0})
        rules_cache.invalidate()
        self._load_rules_to_cache()

    def search_rules(self, keyword: str) -> list[dict]:
        """Tìm kiếm luật theo từ khóa."""
        keyword_lower = keyword.lower()
        results = []
        for rule in self.get_all_rules():
            if (keyword_lower in rule.get("name", "").lower() or 
                keyword_lower in rule.get("description", "").lower() or
                keyword_lower in rule.get("target_major", "").lower()):
                results.append(rule)
        return results

    def validate_rule(self, rule: dict) -> tuple[bool, str]:
        """Kiểm tra tính hợp lệ của luật."""
        # Check required fields
        required = ["name", "conditions", "action_type", "target_major", "weight"]
        for field in required:
            if field not in rule or not rule[field]:
                return False, f"Thiếu trường bắt buộc: {field}"
        
        # Check conditions format
        if not isinstance(rule.get("conditions"), (list, dict)):
            return False, "Điều kiện phải là danh sách hoặc từ điển"
        
        # Check action_type
        if rule["action_type"] not in ["boost", "exclude"]:
            return False, "Loại hành động phải là 'boost' hoặc 'exclude'"
        
        # Check weight range
        try:
            weight = float(rule.get("weight", 0))
            if not 0 <= weight <= 1:
                return False, "Trọng số phải nằm trong khoảng 0-1"
        except ValueError:
            return False, "Trọng số phải là số"
        
        return True, "OK"

    def infer(self, scores: dict) -> tuple[dict[str, float], list]:
        """
        Suy diễn từ tập luật.
        
        Returns:
            (probability dict per major, list of fired rules with details)
        """
        import json
        
        # Khởi tạo xác suất cho mỗi chuyên ngành
        expert_proba = {major: 0.0 for major in MAJORS}
        fired_rules = []

        # Lấy rules từ cache (tối ưu hơn truy vấn DB)
        all_rules = rules_cache.get_all()

        for rule in all_rules:
            if not rule.get("active", True):
                continue

            # Parse conditions từ string nếu cần
            conditions = rule.get("conditions", [])
            if isinstance(conditions, str):
                try:
                    conditions = json.loads(conditions)
                except:
                    conditions = []

            # Kiểm tra điều kiện
            if self._check_conditions(rule, scores, conditions):
                fired_rules.append(
                    {
                        "rule_id": rule.get("id", 0),
                        "name": rule["name"],
                        "description": rule["description"],
                        "action_type": rule["action_type"],
                        "target_major": rule["target_major"],
                        "weight": rule["weight"],
                    }
                )

                # Áp dụng action
                major = rule["target_major"]
                weight = rule["weight"]

                if rule["action_type"] == "boost":
                    expert_proba[major] += weight
                elif rule["action_type"] == "exclude":
                    expert_proba[major] = 0.0

        # Normalize xác suất
        total = sum(expert_proba.values())
        if total > 0:
            expert_proba = {k: round(v / total, 4) for k, v in expert_proba.items()}
        else:
            # Nếu không có luật được kích hoạt, uniform distribution
            expert_proba = {major: round(1.0 / len(MAJORS), 4) for major in MAJORS}

        return expert_proba, fired_rules

    def _check_conditions(self, rule: dict, scores: dict, conditions: list = None) -> bool:
        """Kiểm tra xem điều kiện của luật có thỏa mãn không."""
        if conditions is None:
            conditions = rule.get("conditions", [])
        
        logic = rule.get("logic", "AND")

        if logic == "AND":
            return all(self._eval_condition(cond, scores) for cond in conditions)
        elif logic == "OR":
            return any(self._eval_condition(cond, scores) for cond in conditions)
        return False

    @staticmethod
    def _eval_condition(condition: dict, scores: dict) -> bool:
        """Đánh giá một điều kiện đơn."""
        course = condition["course"]
        operator = condition["operator"]
        value = condition["value"]
        score = scores.get(course, 0.0)

        if operator not in OPERATORS:
            return False

        return OPERATORS[operator](score, value)
