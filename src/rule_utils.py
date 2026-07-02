"""Tiện ích parse và chuẩn hóa luật chuyên gia."""

from __future__ import annotations

import ast
import json
from typing import Any


def parse_conditions(raw: Any) -> list[dict]:
    """Chuyển conditions từ JSON string / list sang list dict."""
    if isinstance(raw, list):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            try:
                parsed = ast.literal_eval(raw)
            except (ValueError, SyntaxError):
                return []
        return parsed if isinstance(parsed, list) else []
    return []


def normalize_rule(rule: dict) -> dict:
    """Chuẩn hóa rule từ SQLite (parse conditions, thêm doc_id)."""
    result = dict(rule)
    result["conditions"] = parse_conditions(result.get("conditions"))
    result["doc_id"] = result.get("id", result.get("doc_id"))
    if "active" in result:
        result["active"] = bool(result["active"])
    return result
