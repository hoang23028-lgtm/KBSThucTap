"""Hệ chuyên gia tối ưu với SQLite + caching."""

from __future__ import annotations

import ast
import json
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
    """Luật chuyên gia khởi tạo theo tri thức miền CNTT và dữ liệu thực tế."""
    return [
        {
            "name": "DS - Thống kê cao",
            "description": "Điểm Thống kê cơ bản >= 80 → tăng Khoa học Dữ liệu",
            "conditions": [
                {"course": "Basic Statistics", "operator": ">=", "value": 90},
                {"course": "Linear Algebra", "operator": ">=", "value": 82},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "DATA SCIENCE",
            "weight": 0.14,
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
            "name": "DS - Toán cao",
            "description": "Đại số tuyến tính >= 82 VÀ Giải tích >= 90 → tăng Khoa học Dữ liệu",
            "conditions": [
                {"course": "Linear Algebra", "operator": ">=", "value": 82},
                {"course": "Calculus", "operator": ">=", "value": 90},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "DATA SCIENCE",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "IS - AI cao",
            "description": "Điểm AI >= 90 → tăng Hệ thống Thông minh",
            "conditions": [{"course": "Artificial Intelligence", "operator": ">=", "value": 90}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "INTELLIGENT SYSTEM",
            "weight": 0.08,
            "active": True,
        },
        {
            "name": "IS - AI + Thuật toán",
            "description": "AI >= 90 VÀ Thiết kế thuật toán >= 78 → tăng Hệ thống Thông minh",
            "conditions": [
                {"course": "Artificial Intelligence", "operator": ">=", "value": 90},
                {"course": "Algorithm Design and Analysis", "operator": ">=", "value": 78},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "INTELLIGENT SYSTEM",
            "weight": 0.08,
            "active": True,
        },
        {
            "name": "IS - AI + Mạng",
            "description": "AI >= 90 VÀ Mạng máy tính >= 78 → tăng Hệ thống Thông minh",
            "conditions": [
                {"course": "Artificial Intelligence", "operator": ">=", "value": 90},
                {"course": "Computer Networks", "operator": ">=", "value": 78},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "INTELLIGENT SYSTEM",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "NET - Mạng rất cao",
            "description": "Điểm Mạng máy tính >= 90 → tăng Công nghệ Mạng",
            "conditions": [{"course": "Computer Networks", "operator": ">=", "value": 90}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "NETWORK TECHNOLOGY",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "NET - HĐH + Mạng rất cao",
            "description": "Hệ điều hành >= 70 VÀ Mạng >= 90 → tăng Công nghệ Mạng",
            "conditions": [
                {"course": "Operating System", "operator": ">=", "value": 70},
                {"course": "Computer Networks", "operator": ">=", "value": 90},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "NETWORK TECHNOLOGY",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "DB - CSDL rất cao",
            "description": "Điểm Công nghệ CSDL >= 90 → tăng Công nghệ CSDL",
            "conditions": [{"course": "Database Technology", "operator": ">=", "value": 90}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "DATABASE TECHNOLOGY",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "DB - CSDL + OOP",
            "description": "CSDL >= 90 VÀ OOP >= 85 → tăng Công nghệ CSDL",
            "conditions": [
                {"course": "Database Technology", "operator": ">=", "value": 90},
                {"course": "Object Oriented Programming", "operator": ">=", "value": 85},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "DATABASE TECHNOLOGY",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "DB - CSDL + CTDL",
            "description": "CSDL >= 90 VÀ Cấu trúc dữ liệu >= 75 → tăng Công nghệ CSDL",
            "conditions": [
                {"course": "Database Technology", "operator": ">=", "value": 90},
                {"course": "Data Structures", "operator": ">=", "value": 75},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "DATABASE TECHNOLOGY",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "IoT - Mạng + CSDL chuẩn",
            "description": "Mạng máy tính >= 82 VÀ CSDL >= 88 → tăng IoT",
            "conditions": [
                {"course": "Computer Networks", "operator": ">=", "value": 82},
                {"course": "Database Technology", "operator": ">=", "value": 88},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "INTERNET OF THINGS",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "IoT - Mạng + CSDL mở rộng",
            "description": "Mạng máy tính >= 85 VÀ CSDL >= 85 → tăng IoT",
            "conditions": [
                {"course": "Computer Networks", "operator": ">=", "value": 85},
                {"course": "Database Technology", "operator": ">=", "value": 85},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "INTERNET OF THINGS",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "GAME - Web + OOP",
            "description": "Web >= 78 VÀ OOP >= 78 → tăng Công nghệ Game",
            "conditions": [
                {"course": "Web Development", "operator": ">=", "value": 85},
                {"course": "Object Oriented Programming", "operator": ">=", "value": 85},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "GAME TECHNOLOGY",
            "weight": 0.06,
            "active": False,
        },
        {
            "name": "GAME - ATP + CTDL + Mạng",
            "description": "Thuật toán và Lập trình >= 80 VÀ Cấu trúc dữ liệu >= 82 VÀ Mạng máy tính >= 80 → tăng Công nghệ Game",
            "conditions": [
                {"course": "Algorithm and Programming", "operator": ">=", "value": 82},
                {"course": "Data Structures", "operator": ">=", "value": 82},
                {"course": "Computer Networks", "operator": ">=", "value": 80},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "GAME TECHNOLOGY",
            "weight": 0.22,
            "active": True,
        },
        {
            "name": "GAME - Web + OOP + ATP",
            "description": "Web >= 80 VÀ OOP >= 90 VÀ Thuật toán và Lập trình >= 85 → tăng Công nghệ Game",
            "conditions": [
                {"course": "Web Development", "operator": ">=", "value": 82},
                {"course": "Object Oriented Programming", "operator": ">=", "value": 90},
                {"course": "Algorithm and Programming", "operator": ">=", "value": 86},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "GAME TECHNOLOGY",
            "weight": 0.18,
            "active": False,
        },
        {
            "name": "SE - Thiết kế chương trình",
            "description": "Program Design Methods >= 88 VÀ OOP >= 85 → tăng Kỹ thuật Phần mềm",
            "conditions": [
                {"course": "Program Design Methods", "operator": ">=", "value": 88},
                {"course": "Object Oriented Programming", "operator": ">=", "value": 85},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "SOFTWARE ENGINEERING",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "SE - OOP cao",
            "description": "OOP >= 90 → tăng Kỹ thuật Phần mềm",
            "conditions": [{"course": "Object Oriented Programming", "operator": ">=", "value": 90}],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "SOFTWARE ENGINEERING",
            "weight": 0.12,
            "active": True,
        },
        {
            "name": "SE - Thuật toán + CTDL + OOP",
            "description": "Thuật toán và Lập trình >= 88 VÀ Cấu trúc dữ liệu >= 80 VÀ OOP >= 85 → tăng Kỹ thuật Phần mềm",
            "conditions": [
                {"course": "Algorithm and Programming", "operator": ">=", "value": 88},
                {"course": "Data Structures", "operator": ">=", "value": 80},
                {"course": "Object Oriented Programming", "operator": ">=", "value": 85},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "SOFTWARE ENGINEERING",
            "weight": 0.18,
            "active": True,
        },
        {
            "name": "SE - Thuật toán cao",
            "description": "Thuật toán và Lập trình >= 90 VÀ Phương pháp thiết kế CT >= 80 → tăng Kỹ thuật Phần mềm",
            "conditions": [
                {"course": "Algorithm and Programming", "operator": ">=", "value": 90},
                {"course": "Program Design Methods", "operator": ">=", "value": 80},
            ],
            "logic": "AND",
            "action_type": "boost",
            "target_major": "SOFTWARE ENGINEERING",
            "weight": 0.18,
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
            "active": False,
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
        all_rules = self.db.all()
        
        # Parse conditions từ string (nếu từ SQLite)
        for rule in all_rules:
            conds = rule.get("conditions")
            if isinstance(conds, str):
                try:
                    rule["conditions"] = json.loads(conds)
                except json.JSONDecodeError:
                    try:
                        rule["conditions"] = ast.literal_eval(conds)
                    except Exception:
                        rule["conditions"] = []
        
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
                except json.JSONDecodeError:
                    try:
                        rule_copy["conditions"] = ast.literal_eval(rule_copy["conditions"])
                    except Exception:
                        rule_copy["conditions"] = []
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
        
            "conditions": [{"course": "Object Oriented Programming", "operator": ">=", "value": 90}],
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
                except json.JSONDecodeError:
                    try:
                        conditions = ast.literal_eval(conditions)
                    except Exception:
                        conditions = []

            if not isinstance(conditions, list):
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

        if not conditions:
            return False

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
