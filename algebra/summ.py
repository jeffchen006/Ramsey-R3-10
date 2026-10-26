"""Summarize otabu/subtabu logs: best (tri, c10, c9) per class. usage: summ.py PREFIX"""
import glob, re, sys, collections
pre = sys.argv[1] if len(sys.argv) > 1 else 'L_'
best = collections.defaultdict(list)
for fn in glob.glob(f'../runs/algebra/{pre}*.log'):
    cls = re.sub(r'_s\d+\.log$', '', fn.split('/')[-1])
    rows = [l for l in open(fn) if l.startswith('it ')]
    found = any('FOUND' in l for l in open(fn))
    if not rows: best[cls].append((9e9, 9e9, 0, found)); continue
    m = re.search(r'tri=(\d+) c10=(\d+) c9=(\d+)', rows[-1])
    best[cls].append((int(m.group(1)), int(m.group(2)), int(m.group(3)), found))
for cls in sorted(best):
    v = sorted(best[cls])
    print(f"{cls:28s} runs={len(v)} best tri={v[0][0]} c10={v[0][1]} c9={v[0][2]} all_c10={[x[1] for x in v]}" + (" FOUND" if any(x[3] for x in v) else ""))
