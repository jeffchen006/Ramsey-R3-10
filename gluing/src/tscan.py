# scan increment vectors t_d for (3,k;n,<=emax); fast LP-relaxation filter (sufficient), then
# exact integer check (tcheck.check) for the cheapest candidates. Rank by number of input graphs.
import sys, itertools
from fractions import Fraction as Fr
sys.path.insert(0, 'src')
from tcheck import check, e3
C = {22: [21, 1521, 72353, 2331462], 23: [102, 8241, 356041, 10326716],
     24: [51, 3419, 129347, 3288695, 64233886], 25: [396, 21493, 613285, 11946369],
     26: [62, 1625, 23409, 216151, 1526296], 27: [4, 92, 1374, 11915, 52807, 122419, 151308, 99332, 33145, 4746]}
k, n, emax = map(int, sys.argv[1:4])
degs = [d for d in range(0, k) if 0 <= n - d - 1 and e3(k - 1, n - d - 1) < 10 ** 9]
var = [d for d in degs if (n - d - 1) in C]
def lpmax(td):
    w = {d: Fr(n * d, 2) - d * d - e3(k - 1, n - d - 1) - td.get(d, 0) for d in degs}
    best = None
    for d in degs:
        if d * n <= 2 * emax:
            v = n * w[d]; best = v if best is None or v > best else best
    for a in degs:
        for b in degs:
            if a < b:
                nb = Fr(2 * emax - a * n, b - a); na = n - nb
                if 0 <= nb <= n:
                    v = na * w[a] + nb * w[b]; best = v if best is None or v > best else best
    return best
res = []
for t in itertools.product(*[range(0, len(C[n - d - 1]) + 1) for d in var]):
    td = dict(zip(var, t))
    if lpmax(td) < 0:
        res.append((sum(sum(C[n - d - 1][:td[d]]) for d in var), td))
res.sort(key=lambda x: x[0])
for cost, td in res[:8]:
    f, bad = check(k, n, emax, td)
    print(cost, {d: v for d, v in td.items() if v}, 'exact OK' if not bad else 'exact FAIL')
