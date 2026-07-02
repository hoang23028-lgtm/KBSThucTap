"""Phân tích chất lượng luật chuyên gia trên dữ liệu huấn luyện."""

import _bootstrap  # noqa: F401

from collections import Counter

from src.data_loader import load_raw_data, pivot_student_scores
from src.expert_system import ExpertSystem
from src.rule_utils import parse_conditions

raw = load_raw_data()
pivot = pivot_student_scores(raw)
expert = ExpertSystem()
rules = expert.get_all_rules()

for rule in rules:
    conds = parse_conditions(rule["conditions"])
    matched = pivot
    for cond in conds:
        course = cond["course"]
        op = cond["operator"]
        val = cond["value"]
        if op == ">=":
            matched = matched[matched[course] >= val]
        elif op == ">":
            matched = matched[matched[course] > val]
        elif op == "<=":
            matched = matched[matched[course] <= val]
        elif op == "<":
            matched = matched[matched[course] < val]
        elif op == "==":
            matched = matched[matched[course] == val]
    counts = Counter(matched["major"])
    total = len(matched)
    target_count = counts[rule["target_major"]]
    ratio = target_count / total if total else 0
    print(
        f"Rule {rule['doc_id']} {rule['name']} ({rule['action_type']} -> {rule['target_major']}): "
        f"total={total}, target_count={target_count}, ratio={ratio:.3f}"
    )
    print("  top majors", counts.most_common(5))
    print("  conds", conds)
    print()
