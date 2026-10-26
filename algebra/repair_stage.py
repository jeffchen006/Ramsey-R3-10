"""Pick the best seeds (lowest c10, triangle-free) among runs/algebra/{L_,P_}*.best and write repair jobs:
unrestricted otabu (every pair its own class) started from the seed, 30 min each."""
import glob, sys
sys.path.insert(0, './algebra')
import ev
cands = []
for fn in glob.glob('../runs/algebra/L_*.best') + glob.glob('../runs/algebra/P_*.best'):
    a = ev.from_graph6(open(fn).readline())
    if len(a) != 40 or ev.tri(a): continue
    cands.append((ev.indep(a, 10), ev.indep(a, 9), fn))
cands.sort()
# one seed per class (distinct prefix without _sN)
import re
seen = set(); pick = []
for c in cands:
    cls = re.sub(r'_s\d+\.best$', '', c[2])
    if cls in seen: continue
    seen.add(cls); pick.append(c)
    if len(pick) == 16: break
with open('jobs_repair.txt', 'w') as f:
    for i, (c10, c9, fn) in enumerate(pick):
        tag = fn.split('/')[-1][:-5]
        f.write(f"timeout 1800 ./otabu orb/n40_none.txt {i+1} 1000000000 20 50 0 ../runs/algebra/R_{tag} 3000 0.03 {fn} > ../runs/algebra/R_{tag}.log 2>&1\n")
        print(c10, c9, fn)
