"""Hệ chuyên gia với SQLite + caching."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from src.cache import rules_cache
from src.config import MAJORS, RULES_DB
from src.database import open_db
from src.default_rules import default_rules
from src.rule_utils import normalize_rule, parse_conditions

OPERATORS = {
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "<=": lambda a, b: a <= b,
    "<": lambda a, b: a < b,
    "==": lambda a, b: a == b,
}


class ExpertSystem:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or RULES_DB
        self.db = open_db(self.db_path)

        if self.db.count() == 0:
            self.seed_default_rules()

        self._load_rules_to_cache()

    def _load_rules_to_cache(self) -> None:
        rules_cache.load([normalize_rule(r) for r in self.db.all()])

    def seed_default_rules(self) -> int:
        self.db.truncate()
        for rule in default_rules():
            rule_copy = rule.copy()
            rule_copy["conditions"] = json.dumps(rule_copy["conditions"])
            self.db.insert(rule_copy)
        return self.db.count()

    def get_all_rules(self) -> list[dict]:
        return [normalize_rule(r) for r in rules_cache.get_all()]

    def add_rule(self, rule: dict) -> int:
        rule_copy = rule.copy()
        rule_copy["conditions"] = json.dumps(rule_copy["conditions"])
        rule_id = self.db.insert(rule_copy)
        rules_cache.invalidate()
        self._load_rules_to_cache()
        return rule_id

    def update_rule(self, rule_id: int, updates: dict) -> None:
        self.db.update(rule_id, updates)
        rules_cache.invalidate()
        self._load_rules_to_cache()

    def delete_rule(self, rule_id: int) -> None:
        self.db.remove(rule_id)
        rules_cache.invalidate()
        self._load_rules_to_cache()

    def get_rule(self, rule_id: int) -> Optional[dict]:
        row = self.db.get_by_id(rule_id)
        return normalize_rule(row) if row else None

    def toggle_rule(self, rule_id: int, active: bool) -> None:
        self.db.update(rule_id, {"active": active})
        rules_cache.invalidate()
        self._load_rules_to_cache()

    def search_rules(self, keyword: str) -> list[dict]:
        keyword_lower = keyword.lower()
        return [
            rule
            for rule in self.get_all_rules()
            if keyword_lower in rule.get("name", "").lower()
            or keyword_lower in rule.get("description", "").lower()
            or keyword_lower in rule.get("target_major", "").lower()
        ]

    def validate_rule(self, rule: dict) -> tuple[bool, str]:
        required = ["name", "conditions", "action_type", "target_major", "weight"]
        for field in required:
            if field not in rule or rule[field] in (None, "", []):
                return False, f"Thiếu trường bắt buộc: {field}"

        if not isinstance(rule.get("conditions"), (list, dict)):
            return False, "Điều kiện phải là danh sách hoặc từ điển"

        if rule["action_type"] not in ("boost", "exclude"):
            return False, "Loại hành động phải là 'boost' hoặc 'exclude'"

        try:
            weight = float(rule.get("weight", 0))
            if not 0 <= weight <= 1:
                return False, "Trọng số phải nằm trong khoảng 0-1"
        except (TypeError, ValueError):
            return False, "Trọng số phải là số"

        return True, "OK"

    def infer(self, scores: dict) -> tuple[dict[str, float], list]:
        """Suy diễn: trả về (xác suất theo ngành, danh sách luật kích hoạt)."""
        expert_proba = {major: 0.0 for major in MAJORS}
        fired_rules = []

        for rule in rules_cache.get_all():
            if not rule.get("active", True):
                continue

            conditions = rule.get("conditions") or []
            if not isinstance(conditions, list):
                conditions = parse_conditions(conditions)

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

                major = rule["target_major"]
                if rule["action_type"] == "boost":
                    expert_proba[major] += rule["weight"]
                elif rule["action_type"] == "exclude":
                    expert_proba[major] = 0.0

        total = sum(expert_proba.values())
        if total > 0:
            expert_proba = {k: round(v / total, 4) for k, v in expert_proba.items()}
        else:
            expert_proba = {major: round(1.0 / len(MAJORS), 4) for major in MAJORS}

        return expert_proba, fired_rules

    def _check_conditions(
        self, rule: dict, scores: dict, conditions: list | None = None
    ) -> bool:
        if conditions is None:
            conditions = rule.get("conditions", [])

        if not conditions:
            return False

        logic = rule.get("logic", "AND")
        if logic == "AND":
            return all(self._eval_condition(cond, scores) for cond in conditions)
        if logic == "OR":
            return any(self._eval_condition(cond, scores) for cond in conditions)
        return False

    @staticmethod
    def _eval_condition(condition: dict, scores: dict) -> bool:
        course = condition["course"]
        operator = condition["operator"]
        value = condition["value"]
        score = scores.get(course, 0.0)

        if operator not in OPERATORS:
            return False

        return OPERATORS[operator](score, value)
