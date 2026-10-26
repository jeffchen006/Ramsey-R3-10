"""Cheapest GR increments t_d for generating R(3,k;n,<=emax) from R(3,k-1;n-d-1, <= e(3,k-1,n-d-1)+t_d-1).
Cost = number of input graphs, from per-level counts (exact GR/McKay where known, else MCMC estimate).
Feasibility = LP relaxation of the GR inequality (4) (sufficient condition; see tcheck.py).
Branch and bound over t_d. usage: python3 topt.py k n emax [maxinc]
"""
import sys, math
from fractions import Fraction as Fr
sys.path.insert(0, 'src')
from tcheck import e3

R = '../runs/gluing'
def mc_levels(n, e0, L0):
    import subprocess
    out = subprocess.run(['python3', 'src/combine.py', str(e0), str(L0), f'{R}/mc38_n{n}.out'],
                         capture_output=True, text=True).stdout.split('\n')[1:]
    return [float(l.split('|')[1].split()[0]) for l in out if '|' in l]
# per-level counts for R(3,8;m,e(3,8,m)+i), i = 0,1,...
EX = {22: [21, 1521, 72353, 2331462], 23: [102, 8241, 356041, 10326716], 24: [51, 3419, 129347, 3288695, 64233886],
      25: [396, 21493, 613285, 11946369], 26: [62, 1625, 23409, 216151, 1526296],
      27: [4, 92, 1374, 11915, 52807, 122419, 151308, 99332, 33145, 4746]}
anch = {int(l.split()[0]): (int(l.split()[1]), float(l.split()[2])) for l in open(f'{R}/r38_anchor.txt')}
C = {}
for m in range(22, 28):
    lv = list(EX[m])
    if m in anch and m != 27:
        est = mc_levels(m, *anch[m])
        lv += est[len(lv):]
    C[m] = lv

k, n, emax = map(int, sys.argv[1:4]); MAXI = int(sys.argv[4]) if len(sys.argv) > 4 else 14
degs = [d for d in range(0, k) if n - d - 1 >= 0 and e3(k - 1, n - d - 1) < 10 ** 9]
w = {d: Fr(n * d, 2) - d * d - e3(k - 1, n - d - 1) for d in degs}
# extreme points of {n_d >= 0, sum n_d = n, sum d n_d <= 2 emax}: single degrees and pairs on the edge face
pts = []
for d in degs:
    if d * n <= 2 * emax: pts.append({d: Fr(n)})
for a in degs:
    for b in degs:
        if a < b:
            nb = Fr(2 * emax - a * n, b - a)
            if 0 <= nb <= n: pts.append({a: n - nb, b: nb})
def cost(d, t):
    m = n - d - 1
    if t == 0: return 0
    if m not in C or t > len(C[m]): return math.inf
    return sum(C[m][:t])
order = sorted(degs, key=lambda d: -max((p.get(d, 0) for p in pts), default=0))
best = [math.inf, None]
def ok_partial(t):
    # each point needs sum p_d (w_d - t_d) < 0; undecided t_d may still grow up to MAXI
    for p in pts:
        s = sum(c * (w[d] - (t[d] if d in t else (MAXI if (n - d - 1) in C else 0))) for d, c in p.items())
        if s >= 0: return False
    return True
def rec(i, t, c):
    if c >= best[0] or not ok_partial(t): return
    if i == len(order):
        best[0], best[1] = c, dict(t); return
    d = order[i]
    for v in range(0, MAXI + 1):
        cc = cost(d, v)
        if cc == math.inf: break
        t[d] = v; rec(i + 1, t, c + cc); del t[d]
rec(0, {}, 0)
t = best[1]
print(f'R(3,{k};{n},<={emax}): min inputs {best[0]:.3g} with t = { {d: v for d, v in t.items() if v} }')
for d in sorted(t):
    if t[d]:
        m = n - d - 1
        print(f'   d={d}: R(3,{k-1};{m},<={e3(k-1,m)+t[d]-1})  {cost(d, t[d]):.3g} graphs')
