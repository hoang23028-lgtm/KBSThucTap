import json
import ast
import sys
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import load_raw_data, pivot_student_scores
from src.expert_system_v2 import ExpertSystem

raw = load_raw_data()
pivot = pivot_student_scores(raw)
expert = ExpertSystem()
rules = expert.get_all_rules()

for rule in rules:
    conds = rule["conditions"]
    if isinstance(conds, str):
        try:
            conds = json.loads(conds)
        except json.JSONDecodeError:
            conds = ast.literal_eval(conds)
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
    print(f"Rule {rule['doc_id']} {rule['name']} ({rule['action_type']} -> {rule['target_major']}): total={total}, target_count={target_count}, ratio={ratio:.3f}")
    print('  top majors', counts.most_common(5))
    print('  conds', conds)
    print()