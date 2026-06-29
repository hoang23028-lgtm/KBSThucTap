"""Grid search for GAME rule thresholds and report best candidates."""
import json
from pathlib import Path
from collections import Counter
import itertools
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data_loader import load_raw_data, pivot_student_scores

raw = load_raw_data()
pivot = pivot_student_scores(raw)

# Define grids
atp_vals = [82, 84, 86, 88]
ctdl_vals = [80, 82, 84, 86]
net_vals = [80, 82, 84]

web_vals = [80, 82, 84]
oop_vals = [88, 90, 92]
atp2_vals = [84, 86, 88]

candidates = []
min_total = 5

# ATP+CTDL+Networks combos
for a, d, n in itertools.product(atp_vals, ctdl_vals, net_vals):
    matched = pivot[(pivot['Algorithm and Programming'] >= a) & (pivot['Data Structures'] >= d) & (pivot['Computer Networks'] >= n)]
    total = len(matched)
    if total == 0:
        continue
    cnt = Counter(matched['major'])
    target = cnt['GAME TECHNOLOGY']
    ratio = target / total if total else 0
    candidates.append(('ATP+CTDL+Net', f'ATP>={a} CTDL>={d} Net>={n}', total, target, ratio))

# Web+OOP+ATP combos
for w, o, a in itertools.product(web_vals, oop_vals, atp2_vals):
    matched = pivot[(pivot['Web Development'] >= w) & (pivot['Object Oriented Programming'] >= o) & (pivot['Algorithm and Programming'] >= a)]
    total = len(matched)
    if total == 0:
        continue
    cnt = Counter(matched['major'])
    target = cnt['GAME TECHNOLOGY']
    ratio = target / total if total else 0
    candidates.append(('Web+OOP+ATP', f'Web>={w} OOP>={o} ATP>={a}', total, target, ratio))

# Sort by ratio desc, then total desc
candidates.sort(key=lambda x: (x[4], x[2]), reverse=True)

print('Top candidate combos (min_total=', min_total, '):')
for kind, desc, total, target, ratio in candidates[:30]:
    print(f'{kind}: {desc} => total={total}, target={target}, ratio={ratio:.3f}')

# Filter by min_total and show best
filtered = [c for c in candidates if c[2] >= min_total]
if filtered:
    print('\nBest with total>={}:'.format(min_total))
    kind, desc, total, target, ratio = filtered[0]
    print(kind, desc, total, target, ratio)
else:
    print('\nNo candidate meets min_total=', min_total)
    print('Showing top 5 overall instead:')
    for c in candidates[:5]:
        print(c)
